# Terraform configuration for WordPress - Cost Efficient Setup
# Generated on: 2025-03-23 17:26:38
# This file was assembled from modular components


provider "aws" {
  region = var.aws_region
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}



# VPC Configuration
resource "aws_vpc" "wordpress_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  
  tags = {
    Name = "${var.project_name}-vpc"
  }
}



# EC2 Instance for WordPress
resource "aws_instance" "wordpress" {
  ami                    = var.instance_ami
  instance_type          = var.instance_type
  key_name               = var.key_name
  subnet_id              = aws_subnet.wordpress_public_subnet.id
  vpc_security_group_ids = [aws_security_group.wordpress_sg.id]
  
  root_block_device {
    volume_size = var.instance_volume_size
    volume_type = "gp3"
  }
  
  user_data = <<-EOF
{user_data_script}
  EOF
  
  tags = {
    Name = "${var.project_name}-instance"
  }
}



# Application Load Balancer
resource "aws_lb" "wordpress_lb" {
  name               = "${var.project_name}-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [{security_groups}]
  subnets            = [{subnets}]
  
  tags = {
    Name = "${var.project_name}-lb"
  }
}


# Outputs
