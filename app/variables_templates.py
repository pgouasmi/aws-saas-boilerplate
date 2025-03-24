VARIABLE_TEMPLATES = {
    "aws": """
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "{aws_region}"
}

variable "aws_access_key" {
  description = "AWS access key"
  type        = string
  default     = "{aws_access_key}"
  sensitive   = true
}

variable "aws_secret_key" {
  description = "AWS secret key"
  type        = string
  default     = "{aws_secret_key}"
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
""",
    
    # Autres groupes de variables
}