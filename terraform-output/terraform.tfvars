# Terraform variable values for WordPress - Cost Efficient Setup
# Generated on: 2025-03-23 17:26:38
# These values are generated from your .env file

# AWS Configuration
aws_region         = "us-east-1"

# Project Configuration
project_name       = "wordpress-site"
environment        = "dev"

# Network Configuration
vpc_cidr           = "10.0.0.0/16"
subnet_cidr        = "10.0.1.0/24"
allowed_ssh_ips    = ["0.0.0.0/0"]
allowed_http_ips   = ["0.0.0.0/0"]

# EC2 Configuration
instance_type      = "t3.micro"
instance_ami       = "ami-0df435f331839b2d6"
instance_volume_size = 20

# WordPress Configuration
wordpress_domain     = "example.com"
wordpress_db_name    = "wordpress"
wordpress_db_user    = "wordpress"
wordpress_db_password = "change-this-password"
wordpress_site_title = "Mon Site WordPress"
wordpress_admin_user = "admin"
wordpress_admin_password = "change-this-admin-password"
wordpress_admin_email = "admin@example.com"
