TERRAFORM_TEMPLATES = {
    "provider": """
provider "aws" {
  region = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}
""",
    
    "vpc": """
# VPC Configuration
resource "aws_vpc" "wordpress_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
}
""",
    
    "security_group": """
# Security Group for {purpose}
resource "aws_security_group" "{sg_name}" {
  name        = "var.project_name-{sg_suffix}"
  description = "Security group for {purpose}"
  vpc_id      = aws_vpc.wordpress_vpc.id
  
{ingress_rules}
  
  # Outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
""",


    "security_group_instance": """
# Security Group for EC2
resource "aws_security_group" "ec2-sg" {
  name        = "var.ec2-sg-name"
  description = "Security group for EC2"
  vpc_id      = aws_vpc.wordpress_vpc.id
  
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
""",


    "security_group_lb": """
# Security Group for Load Balancer
resource "aws_security_group" "lb-sg" {
  name        = "var.lb-sg-name"
  description = "Security group for Load Balancer"
  vpc_id      = aws_vpc.wordpress_vpc.id
  
  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  # Outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
""",

    
    "ec2_instance": """
# EC2 Instance for WordPress
resource "aws_instance" "wordpress" {
  ami                    = var.instance_ami
  instance_type          = var.instance_type
  key_name               = var.ssh_key_name
  vpc_security_group_ids = [aws_security_group.ec2-sg.id]
  subnet_id              = aws_subnet.private_subnet.id
  
  root_block_device {
    volume_size = var.instance_volume_size
    volume_type = "gp3"
  }
  
  user_data = templatefile("./../wordpress-install/user_data.sh.tpl", {
    WORDPRESS_DB_NAME = var.wordpress_db_name,
    WORDPRESS_DB_USER = var.wordpress_db_user,
    WORDPRESS_DB_PASSWORD = var.wordpress_db_password,
    WORDPRESS_SITE_TITLE = var.wordpress_site_title,
    WORDPRESS_ADMIN_USER = var.wordpress_admin_user,
    WORDPRESS_ADMIN_PASSWORD = var.wordpress_admin_password,
    WORDPRESS_ADMIN_EMAIL = var.wordpress_admin_email
    WORDPRESS_INSTALL_PATH = "/var/www/html"
    KEYS_LINE_NUM = ""
    NONCE_SALT_LINE_NUM = ""
    KEYS = ""
  })
  }
""",
    
    "load_balancer": """
# Application Load Balancer
resource "aws_lb" "wordpress_lb" {
  name               = "wordpresslb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb-sg.id]
  subnets              = [aws_subnet.public_subnet.id]
}
""",

"public_subnet": """
# Public Subnet
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.wordpress_vpc.id
  cidr_block              = "{public_subnet_cidr}"
  availability_zone       = "{aws_region}a"
  map_public_ip_on_launch = true
  
  tags = {
    Name = "{project_name}-public-subnet"
    Environment = "{environment}"
  }
}

# Route Table for Public Subnet
resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.wordpress_vpc.id
  
  route {
    cidr_block = "0.0.0.0/0"
  }
  
  tags = {
    Name = "{project_name}-public-rt"
    Environment = "{environment}"
  }
}

# Route Table Association for Public Subnet
resource "aws_route_table_association" "public_rta" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_route_table.id
}
""",

"private_subnet": """
# Private Subnet
resource "aws_subnet" "private_subnet" {
  vpc_id                  = aws_vpc.wordpress_vpc.id
  cidr_block              = "{private_subnet_cidr}"
  availability_zone       = "{aws_region}a"
  map_public_ip_on_launch = false
  
  tags = {
    Name = "{project_name}-private-subnet"
    Environment = "{environment}"
  }
}

# NAT Gateway for Private Subnet (requires an Elastic IP)
resource "aws_eip" "nat_eip" {
  vpc = true
  tags = {
    Name = "{project_name}-nat-eip"
    Environment = "{environment}"
  }
}

resource "aws_nat_gateway" "nat_gateway" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnet.id
  
  tags = {
    Name = "{project_name}-nat-gateway"
    Environment = "{environment}"
  }
}

# Route Table for Private Subnet
resource "aws_route_table" "private_route_table" {
  vpc_id = aws_vpc.wordpress_vpc.id
  
  route {
    cidr_block = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gateway.id
  }
  
  tags = {
    Name = "{project_name}-private-rt"
    Environment = "{environment}"
  }
}

# Route Table Association for Private Subnet
resource "aws_route_table_association" "private_rta" {
  subnet_id      = aws_subnet.private_subnet.id
  route_table_id = aws_route_table.private_route_table.id
}
""",

# "user_data": """
# #!/bin/bash

# LOG_FILE="/var/log/wordpress-install.log"

# log() {
#     echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
# }

# if [ "$(id -u)" -ne 0 ]; then
#     echo "Ce script doit être exécuté avec les privilèges sudo."
#     exit 1
# fi

# WORDPRESS_DB_NAME={wordpress_db_name}
# WORDPRESS_DB_USER={wordpress_db_user}
# WORDPRESS_DB_PASSWORD={wordpress_db_password}
# WORDPRESS_SITE_TITLE={wordpress_site_title}
# WORDPRESS_ADMIN_USER={wordpress_admin_user}
# WORDPRESS_ADMIN_PASSWORD={wordpress_admin_password}
# WORDPRESS_ADMIN_EMAIL={wordpress_admin_email}
# WORDPRESS_INSTALL_PATH="/var/www/html"

# log "Démarrage de l'installation de WordPress sur Amazon Linux 2023"
# log "Domaine/IP: $WORDPRESS_DOMAIN"
# log "Chemin d'installation: $WORDPRESS_INSTALL_PATH"

# log "Mise à jour des paquets système..."
# dnf update -y >> "$LOG_FILE" 2>&1

# log "Installation d'Apache, MariaDB, PHP et autres dépendances..."
# dnf install -y httpd mariadb105-server php php-mysqlnd php-json php-gd php-mbstring php-xml php-intl expect >> "$LOG_FILE" 2>&1

# log "Démarrage et activation des services httpd et mariadb..."
# systemctl start httpd >> "$LOG_FILE" 2>&1
# systemctl start mariadb >> "$LOG_FILE" 2>&1
# systemctl enable httpd >> "$LOG_FILE" 2>&1
# systemctl enable mariadb >> "$LOG_FILE" 2>&1

# log "Attente du démarrage complet de MariaDB..."
# sleep 10

# log "Sécurisation de l'installation MariaDB..."

# expect << EOF
# spawn mysql_secure_installation

# expect "Enter current password for root (enter for none):"
# send "\r"

# expect "Switch to unix_socket authentication"
# send "n\r"

# expect "Change the root password?"
# send "y\r"

# expect "New password:"
# send "$WORDPRESS_DB_PASSWORD\r"

# expect "Re-enter new password:"
# send "$WORDPRESS_DB_PASSWORD\r"

# expect "Remove anonymous users?"
# send "y\r"

# expect "Disallow root login remotely?"
# send "y\r"

# expect "Remove test database and access to it?"
# send "y\r"

# expect "Reload privilege tables now?"
# send "y\r"

# expect eof
# EOF

# log "Création de la base de données WordPress..."
# mysql -u root -p"$WORDPRESS_DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $WORDPRESS_DB_NAME DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# log "Création de l'utilisateur pour WordPress..."
# mysql -u root -p"$WORDPRESS_DB_PASSWORD" <<EOF
# CREATE USER IF NOT EXISTS '$WORDPRESS_DB_USER'@'localhost' IDENTIFIED BY '$WORDPRESS_DB_PASSWORD';
# GRANT ALL PRIVILEGES ON $WORDPRESS_DB_NAME.* TO '$WORDPRESS_DB_USER'@'localhost';
# FLUSH PRIVILEGES;
# EOF

# log "Préparation du répertoire web..."
# mkdir -p $WORDPRESS_INSTALL_PATH
# rm -rf $WORDPRESS_INSTALL_PATH/*

# log "Téléchargement et extraction de WordPress..."
# cd /tmp
# curl -O https://wordpress.org/latest.tar.gz >> "$LOG_FILE" 2>&1
# tar -xzf latest.tar.gz >> "$LOG_FILE" 2>&1
# cp -rf wordpress/* $WORDPRESS_INSTALL_PATH/ >> "$LOG_FILE" 2>&1
# rm -rf wordpress latest.tar.gz

# log "Création du fichier de configuration WordPress..."
# cp $WORDPRESS_INSTALL_PATH/wp-config-sample.php $WORDPRESS_INSTALL_PATH/wp-config.php
# sed -i "s|database_name_here|$WORDPRESS_DB_NAME|g" $WORDPRESS_INSTALL_PATH/wp-config.php
# sed -i "s|username_here|$WORDPRESS_DB_USER|g" $WORDPRESS_INSTALL_PATH/wp-config.php
# sed -i "s|password_here|$WORDPRESS_DB_PASSWORD|g" $WORDPRESS_INSTALL_PATH/wp-config.php
# sed -i "s|localhost|localhost|g" $WORDPRESS_INSTALL_PATH/wp-config.php

# log "Génération des clés de sécurité WordPress..."
# KEYS=$(curl -s https://api.wordpress.org/secret-key/1.1/salt/)
# KEYS_LINE_NUM=$(grep -n "define('AUTH_KEY'" $WORDPRESS_INSTALL_PATH/wp-config.php | cut -d: -f1)
# NONCE_SALT_LINE_NUM=$(grep -n "define('NONCE_SALT'" $WORDPRESS_INSTALL_PATH/wp-config.php | cut -d: -f1)
# if [ -n "$KEYS_LINE_NUM" ] && [ -n "$NONCE_SALT_LINE_NUM" ]; then
#     sed -i "${KEYS_LINE_NUM},${NONCE_SALT_LINE_NUM}d" $WORDPRESS_INSTALL_PATH/wp-config.php
#     sed -i "${KEYS_LINE_NUM}i\\${KEYS}" $WORDPRESS_INSTALL_PATH/wp-config.php
# fi

# log "Installation de WP-CLI..."
# cd /tmp
# curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar >> "$LOG_FILE" 2>&1
# chmod +x wp-cli.phar

# log "Installation de WordPress avec WP-CLI..."
# php /tmp/wp-cli.phar core install --url="http://$WORDPRESS_DOMAIN" \
#                                   --title="$WORDPRESS_SITE_TITLE" \
#                                   --admin_user="$WORDPRESS_ADMIN_USER" \
#                                   --admin_password="$WORDPRESS_ADMIN_PASSWORD" \
#                                   --admin_email="$WORDPRESS_ADMIN_EMAIL" \
#                                   --path="$WORDPRESS_INSTALL_PATH" \
#                                   --allow-root >> "$LOG_FILE" 2>&1

# log "Configuration des permissions..."
# chown -R apache:apache $WORDPRESS_INSTALL_PATH
# find $WORDPRESS_INSTALL_PATH -type d -exec chmod 750 {} \;
# find $WORDPRESS_INSTALL_PATH -type f -exec chmod 640 {} \;
# chmod 400 $WORDPRESS_INSTALL_PATH/wp-config.php

# log "Configuration d'Apache..."
# cat > /etc/httpd/conf.d/wordpress.conf << EOF
# <VirtualHost *:80>
#     ServerAdmin webmaster@$WORDPRESS_DOMAIN
#     DocumentRoot $WORDPRESS_INSTALL_PATH
#     ServerName $WORDPRESS_DOMAIN

#     <Directory $WORDPRESS_INSTALL_PATH>
#         Options FollowSymLinks
#         AllowOverride All
#         Require all granted
#     </Directory>

#     ErrorLog /var/log/httpd/wordpress-error.log
#     CustomLog /var/log/httpd/wordpress-access.log combined
# </VirtualHost>
# EOF

# log "Activation du module rewrite..."
# sed -i 's/#LoadModule rewrite_module modules\/mod_rewrite.so/LoadModule rewrite_module modules\/mod_rewrite.so/' /etc/httpd/conf.modules.d/00-base.conf

# log "Création du fichier .htaccess..."
# cat > $WORDPRESS_INSTALL_PATH/.htaccess << EOF
# # BEGIN WordPress
# <IfModule mod_rewrite.c>
# RewriteEngine On
# RewriteBase /
# RewriteRule ^index\.php$ - [L]
# RewriteCond %{REQUEST_FILENAME} !-f
# RewriteCond %{REQUEST_FILENAME} !-d
# RewriteRule . /index.php [L]
# </IfModule>
# # END WordPress
# EOF

# chown apache:apache $WORDPRESS_INSTALL_PATH/.htaccess
# chmod 644 $WORDPRESS_INSTALL_PATH/.htaccess

# log "Redémarrage d'Apache..."
# systemctl restart httpd >> "$LOG_FILE" 2>&1

# if systemctl is-active --quiet firewalld; then
#     log "Configuration du pare-feu..."
#     firewall-cmd --permanent --add-service=http >> "$LOG_FILE" 2>&1
#     firewall-cmd --permanent --add-service=https >> "$LOG_FILE" 2>&1
#     firewall-cmd --reload >> "$LOG_FILE" 2>&1
# fi

# log "Création d'un fichier de test PHP..."
# echo "<?php phpinfo();" > $WORDPRESS_INSTALL_PATH/info.php
# chown apache:apache $WORDPRESS_INSTALL_PATH/info.php
# chmod 644 $WORDPRESS_INSTALL_PATH/info.php

# echo "==================================================="
# echo "Installation de WordPress terminée !"
# echo "==================================================="
# echo "URL du site: http://$WORDPRESS_DOMAIN"
# echo "URL d'administration: http://$WORDPRESS_DOMAIN/wp-admin/"
# echo "Nom d'utilisateur admin: $WORDPRESS_ADMIN_USER"
# echo "Mot de passe admin: $WORDPRESS_ADMIN_PASSWORD"
# echo "Nom de la base de données: $WORDPRESS_DB_NAME"
# echo "Utilisateur de la base de données: $WORDPRESS_DB_USER"
# echo "Mot de passe de la base de données: $WORDPRESS_DB_PASSWORD"
# echo "(Ces informations sont également enregistrées dans $LOG_FILE)"
# echo "==================================================="
# echo "Pour vérifier que PHP fonctionne: http://$WORDPRESS_DOMAIN/info.php"
# echo "==================================================="

# log "URL du site: http://$WORDPRESS_DOMAIN"
# log "URL d'administration: http://$WORDPRESS_DOMAIN/wp-admin/"
# log "Nom d'utilisateur admin: $WORDPRESS_ADMIN_USER"
# log "Mot de passe admin: $WORDPRESS_ADMIN_PASSWORD"
# log "Nom de la base de données: $WORDPRESS_DB_NAME"
# log "Utilisateur de la base de données: $WORDPRESS_DB_USER"
# log "Mot de passe de la base de données: $WORDPRESS_DB_PASSWORD"
# log "Installation terminée avec succès!"

# """
}