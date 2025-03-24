import os
from dotenv import load_dotenv

def parse_env_file(env_file_path):
    """Parse the .env file and return a dictionary of variables."""
    env_vars = {}
    
    # Set default values for essential variables
    env_vars = {
        # AWS Configuration
        "aws_region": "us-east-1",
        "aws_access_key": "",
        "aws_secret_key": "",
        "aws_session_token": "",
        
        # Network Configuration
        "project_name": "wordpress-site",
        "environment": "dev",
        "vpc_cidr": "10.0.0.0/16",
        "subnet_cidr": "10.0.1.0/24",
        "allowed_ssh_ips": ["0.0.0.0/0"],
        "allowed_http_ips": ["0.0.0.0/0"],
        
        # EC2 Configuration
        "instance_type": "t3.micro",
        "instance_ami": "ami-0df435f331839b2d6",  # Amazon Linux 2023 in us-east-1
        "instance_volume_size": 20,
        "key_name": "",
        
        # WordPress Configuration
        "wordpress_domain": "",
        "wordpress_db_name": "wordpress",
        "wordpress_db_user": "wordpress",
        "wordpress_db_password": "change-this-password",
        "wordpress_site_title": "Mon Site WordPress",
        "wordpress_admin_user": "admin",
        "wordpress_admin_password": "change-this-admin-password",
        "wordpress_admin_email": "admin@example.com",
        "wordpress_install_path": "/var/www/html",
        
        # Optional Configuration for advanced setups
        "wordpress_setup_script_url": "https://raw.githubusercontent.com/yourusername/wordpress-terraform/main/wordpress-setup.sh",
        "enable_s3_media": "false",
        "s3_bucket_name": "",
        "enable_cloudfront": "false",
        "use_rds": "false",
        "rds_instance_class": "db.t3.micro",
        "rds_storage_size": 20,
        "rds_multi_az": "false",
        "enable_auto_scaling": "false",
        "min_instances": 1,
        "max_instances": 3,
        "scale_up_cpu_threshold": 80,
        "scale_down_cpu_threshold": 30,
    }
    
    # If the env file exists, read its values
    if os.path.exists(env_file_path):
        print(f"Reading configuration from {env_file_path}...")
        with open(env_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    try:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Map environment variables to appropriate format
                        if key == "AWS_REGION":
                            env_vars["aws_region"] = value
                        elif key == "AWS_ACCESS_KEY_ID":
                            env_vars["aws_access_key"] = value
                        elif key == "AWS_SECRET_ACCESS_KEY":
                            env_vars["aws_secret_key"] = value
                        elif key == "AWS_SESSION_TOKEN":
                            env_vars["aws_session_token"] = value
                        elif key == "PROJECT_NAME":
                            env_vars["project_name"] = value
                        elif key == "ENVIRONMENT":
                            env_vars["environment"] = value
                        elif key == "CIDR_BLOCK":
                            env_vars["vpc_cidr"] = value
                        elif key == "SUBNET_CIDR_BLOCK":
                            env_vars["subnet_cidr"] = value
                        elif key == "ALLOWED_SSH_CIDR":
                            env_vars["allowed_ssh_ips"] = [value]
                        elif key == "ALLOWED_HTTP_CIDR":
                            env_vars["allowed_http_ips"] = [value]
                        elif key == "EC2_INSTANCE_TYPE":
                            env_vars["instance_type"] = value
                        elif key == "EC2_AMI_ID" and value:  # Only use if not empty
                            env_vars["instance_ami"] = value
                        elif key == "EC2_KEY_PAIR_NAME":
                            env_vars["key_name"] = value
                        elif key == "WORDPRESS_DOMAIN":
                            env_vars["wordpress_domain"] = value
                        elif key == "WORDPRESS_DB_NAME":
                            env_vars["wordpress_db_name"] = value
                        elif key == "WORDPRESS_DB_USER":
                            env_vars["wordpress_db_user"] = value
                        elif key == "WORDPRESS_DB_PASSWORD" and value:  # Only use if not empty
                            env_vars["wordpress_db_password"] = value
                        elif key == "WORDPRESS_SITE_TITLE":
                            env_vars["wordpress_site_title"] = value
                        elif key == "WORDPRESS_ADMIN_USER":
                            env_vars["wordpress_admin_user"] = value
                        elif key == "WORDPRESS_ADMIN_PASSWORD" and value:  # Only use if not empty
                            env_vars["wordpress_admin_password"] = value
                        elif key == "WORDPRESS_ADMIN_EMAIL":
                            env_vars["wordpress_admin_email"] = value
                        elif key == "WORDPRESS_INSTALL_PATH":
                            env_vars["wordpress_install_path"] = value
                        elif key == "USE_RDS":
                            env_vars["use_rds"] = value.lower()
                        elif key == "RDS_INSTANCE_CLASS":
                            env_vars["rds_instance_class"] = value
                        elif key == "RDS_STORAGE_SIZE":
                            try:
                                env_vars["rds_storage_size"] = int(value)
                            except ValueError:
                                pass
                        elif key == "RDS_MULTI_AZ":
                            env_vars["rds_multi_az"] = value.lower()
                        elif key == "ENABLE_AUTO_SCALING":
                            env_vars["enable_auto_scaling"] = value.lower()
                        elif key == "MIN_INSTANCES":
                            try:
                                env_vars["min_instances"] = int(value)
                            except ValueError:
                                pass
                        elif key == "MAX_INSTANCES":
                            try:
                                env_vars["max_instances"] = int(value)
                            except ValueError:
                                pass
                        elif key == "SCALE_UP_CPU_THRESHOLD":
                            try:
                                env_vars["scale_up_cpu_threshold"] = int(value)
                            except ValueError:
                                pass
                        elif key == "SCALE_DOWN_CPU_THRESHOLD":
                            try:
                                env_vars["scale_down_cpu_threshold"] = int(value)
                            except ValueError:
                                pass
                        elif key == "ENABLE_S3_MEDIA":
                            env_vars["enable_s3_media"] = value.lower()
                        elif key == "S3_BUCKET_NAME":
                            env_vars["s3_bucket_name"] = value
                        elif key == "ENABLE_CLOUDFRONT":
                            env_vars["enable_cloudfront"] = value.lower()
                    except ValueError:
                        # Ignore malformed lines
                        continue
    
    # Special processing
    if not env_vars["wordpress_admin_password"]:
        env_vars["wordpress_admin_password"] = env_vars["wordpress_db_password"]
    
    if not env_vars["wordpress_domain"]:
        env_vars["wordpress_domain"] = f"{env_vars['project_name']}.example.com"
    
    return env_vars