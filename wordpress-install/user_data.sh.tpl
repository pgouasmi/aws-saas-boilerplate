#!/bin/bash

LOG_FILE="/var/log/wordpress-install.log"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

if [ "$(id -u)" -ne 0 ]; then
    echo "Ce script doit être exécuté avec les privilèges sudo."
    exit 1
fi

WORDPRESS_DB_NAME="${WORDPRESS_DB_NAME:-wordpress}"
WORDPRESS_DB_USER="${WORDPRESS_DB_USER:-wordpress}"
WORDPRESS_DB_PASSWORD="${WORDPRESS_DB_PASSWORD}"
WORDPRESS_SITE_TITLE="${WORDPRESS_SITE_TITLE:-Mon Site WordPress}"
WORDPRESS_ADMIN_USER="${WORDPRESS_ADMIN_USER:-admin}"
WORDPRESS_ADMIN_PASSWORD="${WORDPRESS_ADMIN_PASSWORD}"
WORDPRESS_ADMIN_EMAIL="${WORDPRESS_ADMIN_EMAIL}"
WORDPRESS_INSTALL_PATH="${WORDPRESS_INSTALL_PATH:-/var/www/html}"

log "Démarrage de l'installation de WordPress sur Amazon Linux 2023"
log "Domaine/IP: $WORDPRESS_DOMAIN"
log "Chemin d'installation: $WORDPRESS_INSTALL_PATH"

log "Mise à jour des paquets système..."
dnf update -y >> "$LOG_FILE" 2>&1

log "Installation d'Apache, MariaDB, PHP et autres dépendances..."
dnf install -y httpd mariadb105-server php php-mysqlnd php-json php-gd php-mbstring php-xml php-intl expect >> "$LOG_FILE" 2>&1

log "Démarrage et activation des services httpd et mariadb..."
systemctl start httpd >> "$LOG_FILE" 2>&1
systemctl start mariadb >> "$LOG_FILE" 2>&1
systemctl enable httpd >> "$LOG_FILE" 2>&1
systemctl enable mariadb >> "$LOG_FILE" 2>&1

log "Attente du démarrage complet de MariaDB..."
sleep 10

log "Sécurisation de l'installation MariaDB..."

expect << EOF
spawn mysql_secure_installation

expect "Enter current password for root (enter for none):"
send "\r"

expect "Switch to unix_socket authentication"
send "n\r"

expect "Change the root password?"
send "y\r"

expect "New password:"
send "$WORDPRESS_DB_PASSWORD\r"

expect "Re-enter new password:"
send "$WORDPRESS_DB_PASSWORD\r"

expect "Remove anonymous users?"
send "y\r"

expect "Disallow root login remotely?"
send "y\r"

expect "Remove test database and access to it?"
send "y\r"

expect "Reload privilege tables now?"
send "y\r"

expect eof
EOF

log "Création de la base de données WordPress..."
mysql -u root -p"$WORDPRESS_DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $WORDPRESS_DB_NAME DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

log "Création de l'utilisateur pour WordPress..."
mysql -u root -p"$WORDPRESS_DB_PASSWORD" <<EOF
CREATE USER IF NOT EXISTS '$WORDPRESS_DB_USER'@'localhost' IDENTIFIED BY '$WORDPRESS_DB_PASSWORD';
GRANT ALL PRIVILEGES ON $WORDPRESS_DB_NAME.* TO '$WORDPRESS_DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

log "Préparation du répertoire web..."
mkdir -p $WORDPRESS_INSTALL_PATH
rm -rf $WORDPRESS_INSTALL_PATH/*

log "Téléchargement et extraction de WordPress..."
cd /tmp
curl -O https://wordpress.org/latest.tar.gz >> "$LOG_FILE" 2>&1
tar -xzf latest.tar.gz >> "$LOG_FILE" 2>&1
cp -rf wordpress/* $WORDPRESS_INSTALL_PATH/ >> "$LOG_FILE" 2>&1
rm -rf wordpress latest.tar.gz

log "Création du fichier de configuration WordPress..."
cp $WORDPRESS_INSTALL_PATH/wp-config-sample.php $WORDPRESS_INSTALL_PATH/wp-config.php
sed -i "s|database_name_here|$WORDPRESS_DB_NAME|g" $WORDPRESS_INSTALL_PATH/wp-config.php
sed -i "s|username_here|$WORDPRESS_DB_USER|g" $WORDPRESS_INSTALL_PATH/wp-config.php
sed -i "s|password_here|$WORDPRESS_DB_PASSWORD|g" $WORDPRESS_INSTALL_PATH/wp-config.php
sed -i "s|localhost|localhost|g" $WORDPRESS_INSTALL_PATH/wp-config.php

log "Génération des clés de sécurité WordPress..."
KEYS=$(curl -s https://api.wordpress.org/secret-key/1.1/salt/)
KEYS_LINE_NUM=$(grep -n "define('AUTH_KEY'" $WORDPRESS_INSTALL_PATH/wp-config.php | cut -d: -f1)
NONCE_SALT_LINE_NUM=$(grep -n "define('NONCE_SALT'" $WORDPRESS_INSTALL_PATH/wp-config.php | cut -d: -f1)
if [ -n "$KEYS_LINE_NUM" ] && [ -n "$NONCE_SALT_LINE_NUM" ]; then
    sed -i "${KEYS_LINE_NUM},${NONCE_SALT_LINE_NUM}d" $WORDPRESS_INSTALL_PATH/wp-config.php
    sed -i "${KEYS_LINE_NUM}i\\${KEYS}" $WORDPRESS_INSTALL_PATH/wp-config.php
fi

log "Installation de WP-CLI..."
cd /tmp
curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar >> "$LOG_FILE" 2>&1
chmod +x wp-cli.phar

log "Installation de WordPress avec WP-CLI..."
php /tmp/wp-cli.phar core install --url="http://$WORDPRESS_DOMAIN" \
                                  --title="$WORDPRESS_SITE_TITLE" \
                                  --admin_user="$WORDPRESS_ADMIN_USER" \
                                  --admin_password="$WORDPRESS_ADMIN_PASSWORD" \
                                  --admin_email="$WORDPRESS_ADMIN_EMAIL" \
                                  --path="$WORDPRESS_INSTALL_PATH" \
                                  --allow-root >> "$LOG_FILE" 2>&1

log "Configuration des permissions..."
chown -R apache:apache $WORDPRESS_INSTALL_PATH
find $WORDPRESS_INSTALL_PATH -type d -exec chmod 750 {} \;
find $WORDPRESS_INSTALL_PATH -type f -exec chmod 640 {} \;
chmod 400 $WORDPRESS_INSTALL_PATH/wp-config.php

log "Configuration d'Apache..."
cat > /etc/httpd/conf.d/wordpress.conf << EOF
<VirtualHost *:80>
    ServerAdmin webmaster@$WORDPRESS_DOMAIN
    DocumentRoot $WORDPRESS_INSTALL_PATH
    ServerName $WORDPRESS_DOMAIN

    <Directory $WORDPRESS_INSTALL_PATH>
        Options FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    ErrorLog /var/log/httpd/wordpress-error.log
    CustomLog /var/log/httpd/wordpress-access.log combined
</VirtualHost>
EOF

log "Activation du module rewrite..."
sed -i 's/#LoadModule rewrite_module modules\/mod_rewrite.so/LoadModule rewrite_module modules\/mod_rewrite.so/' /etc/httpd/conf.modules.d/00-base.conf

log "Création du fichier .htaccess..."
cat > $WORDPRESS_INSTALL_PATH/.htaccess << EOF
# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase /
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.php [L]
</IfModule>
# END WordPress
EOF

chown apache:apache $WORDPRESS_INSTALL_PATH/.htaccess
chmod 644 $WORDPRESS_INSTALL_PATH/.htaccess

log "Redémarrage d'Apache..."
systemctl restart httpd >> "$LOG_FILE" 2>&1

if systemctl is-active --quiet firewalld; then
    log "Configuration du pare-feu..."
    firewall-cmd --permanent --add-service=http >> "$LOG_FILE" 2>&1
    firewall-cmd --permanent --add-service=https >> "$LOG_FILE" 2>&1
    firewall-cmd --reload >> "$LOG_FILE" 2>&1
fi

log "Création d'un fichier de test PHP..."
echo "<?php phpinfo();" > $WORDPRESS_INSTALL_PATH/info.php
chown apache:apache $WORDPRESS_INSTALL_PATH/info.php
chmod 644 $WORDPRESS_INSTALL_PATH/info.php

echo "==================================================="
echo "Installation de WordPress terminée !"
echo "==================================================="
echo "URL du site: http://$WORDPRESS_DOMAIN"
echo "URL d'administration: http://$WORDPRESS_DOMAIN/wp-admin/"
echo "Nom d'utilisateur admin: $WORDPRESS_ADMIN_USER"
echo "Mot de passe admin: $WORDPRESS_ADMIN_PASSWORD"
echo "Nom de la base de données: $WORDPRESS_DB_NAME"
echo "Utilisateur de la base de données: $WORDPRESS_DB_USER"
echo "Mot de passe de la base de données: $WORDPRESS_DB_PASSWORD"
echo "(Ces informations sont également enregistrées dans $LOG_FILE)"
echo "==================================================="
echo "Pour vérifier que PHP fonctionne: http://$WORDPRESS_DOMAIN/info.php"
echo "==================================================="

log "URL du site: http://$WORDPRESS_DOMAIN"
log "URL d'administration: http://$WORDPRESS_DOMAIN/wp-admin/"
log "Nom d'utilisateur admin: $WORDPRESS_ADMIN_USER"
log "Mot de passe admin: $WORDPRESS_ADMIN_PASSWORD"
log "Nom de la base de données: $WORDPRESS_DB_NAME"
log "Utilisateur de la base de données: $WORDPRESS_DB_USER"
log "Mot de passe de la base de données: $WORDPRESS_DB_PASSWORD"
log "Installation terminée avec succès!"