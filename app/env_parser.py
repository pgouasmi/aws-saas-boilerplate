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
        "subnet_cidr": "10.0.0.0/16",
        "public_subnet_cidr": "10.0.0.0/24",
        "private_subnet_cidr": "10.0.1.0/24",
        
        "allowed_ssh_ips": ["0.0.0.0/0"],
        "allowed_http_ips": ["0.0.0.0/0"],
        
        # EC2 Configuration
        "instance_type": "t2.micro",
        "instance_ami": "ami-0eaf62527f5bb8940",  # Amazon Linux 2023 in us-east-1
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
        # print(f"env file path: {}")
        with open(env_file_path, 'r') as f:
            for line in f:
                # print(f"line {line}")
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

                        need_values_keys = ["EC2_AMI_ID", "WORDPRESS_ADMIN_PASSWORD", "WORDPRESS_DB_PASSWORD"]
                        bool_keys = ["USE_RDS", "ENABLE_AUTO_SCALING", "ENABLE_S3_MEDIA", "ENABLE_CLOUDFRONT"]
                        int_keys = ["RDS_STORAGE_SIZE", "MIN_INSTANCES", "MAX_INSTANCES", "SCALE_UP_CPU_THRESHOLD", "SCALE_DOWN_CPU_THRESHOLD", "INSTANCE_VOLUME_SIZE"]
                        
                        # Map environment variables to appropriate format
                        if key in need_values_keys and value:
                            env_vars[key.lower()] = value
                        elif key in bool_keys:
                            env_vars[key.lower()] = value.lower()
                        elif key in int_keys:
                            try:
                                env_vars[key.lower()] = int(value)
                            except ValueError:
                                pass
                        else:
                            env_vars[key.lower()] = value
                    except ValueError:
                        # Ignore malformed lines
                        continue
    
    # Special processing
    if not env_vars["wordpress_admin_password"]:
        env_vars["wordpress_admin_password"] = env_vars["wordpress_db_password"]
    
    if not env_vars["wordpress_domain"]:
        env_vars["wordpress_domain"] = f"{env_vars['project_name']}.example.com"

        print(f"env vars: {env_vars}")
    
    return env_vars