VARIABLE_TEMPLATES = {
    "aws": """
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "{aws_region}"
}

variable "aws_access_key_id" {
  description = "AWS access key"
  type        = string
  default     = "{aws_access_key_id}"
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS secret key"
  type        = string
  default     = "{aws_secret_access_key}"
  sensitive   = true
}
""",
    
    "vpc": """
variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "{vpc_cidr}"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "{public_subnet_cidr}"
}

variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet"
  type        = string
  default     = "{private_subnet_cidr}"
}

variable "lb-sg-name" {
  description = "Load Balancer's security group name"
  type        = string
  default     = "lb-sg"
}

variable "ec2-sg-name" {
  description = "EC2's security group name"
  type        = string
  default     = "ec2-sg"
}

variable "instance_ami" {
  description = "AMI Linux 2023"
  type        = string
  default     = "ami-0eaf62527f5bb8940"
}

variable "instance_type" {
  description = "t2-micro"
  type        = string
  default     = "t2-micro"
}

variable "ssh_key_name" {
  description = "name of the used ssh key"
  type        = string
  default     = ""
}

variable "instance_volume_size" {
  description = "Size of the root EBS volume attached to the EC2 instance"
  type        = number
  default     = {instance_volume_size}
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "{project_name}"
}
""",


    
    # Autres groupes de variables
}