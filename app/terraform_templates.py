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
  
  user_data = <<-EOF
{user_data_script}
  EOF
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
"""
    # Ajoutez d'autres composants comme rds, autoscaling_group, etc.
}