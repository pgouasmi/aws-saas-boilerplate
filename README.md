# AWS WordPress Terraform Generator

A modular Terraform infrastructure generator for deploying WordPress on AWS with different architectures: cost-efficient, high-availability, and custom deployments.

## 📋 Overview

This project enables you to quickly generate Terraform configurations to deploy WordPress on AWS. It offers several predefined architectures, ranging from the most cost-efficient option to highly available configurations for production environments.

The generator uses a modular approach, where infrastructure components, variables, and deployment types are separated, making the code more maintainable and extensible.

### ⚠️⚠️ As of today, the only implemented deployment type is "cost-efficient" (Single EC2 instance, Internet gateway, VPC + public subnet) ⚠️⚠️

## 🚀 Features

- **Multiple deployment options**: Cost-efficient (single EC2), High-availability (multi-AZ, RDS)
- **Configuration via .env file**: Easily customize your deployment
- **Command-line and interactive interface**: Usable in scripts or manually
- **Modular architecture**: Reusable components for different deployment types
- **Automated WordPress installation**: Included installation script

## 🔧 Prerequisites

- Python 3.6 or higher
- Terraform v1.0.0 or higher
- AWS CLI configured with appropriate credentials
- Git (for cloning the repository)

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/aws-wordpress-terraform-generator.git
cd aws-wordpress-terraform-generator

# Install dependencies (if necessary)
pip install -r requirements.txt

# Create and configure the .env file
cp .env.example .env
# Edit the .env file with your settings
```

## 🛠️ Usage

### Interactive Mode

```bash
# Launch the generator in interactive mode
make generate
```

Or directly:

```bash
python app/app.py
```

### Command Line Mode

```bash
# Generate a cost-efficient configuration
make cost-efficient

# Generate a high-availability configuration
make high-availability
```

Or directly with more options:

```bash
python app/app.py --type cost-efficient --output terraform-output
python app/app.py --type high-availability --env custom.env --output terraform-ha
```

## 📁 Project Structure

```
.
├── app/                    # Python application code
│   ├── app.py              # Main script
│   ├── terraform_templates.py  # Terraform component templates
│   ├── variables_templates.py  # Terraform variable templates
│   └── deployment_templates.py # Deployment type definitions
├── wordpress-install/      # WordPress installation scripts
│   └── wordpress-setup.sh  # Main installation script
├── Makefile                # Make targets for easier usage
├── .env.example            # Example environment configuration
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

## ⚙️ Configuration

The `.env` file allows you to configure all aspects of your deployment:

### Basic Configuration
- `AWS_REGION`: AWS region to deploy to
- `PROJECT_NAME`: Name of your project (used for resource naming)
- `WORDPRESS_DOMAIN`: Domain name for your WordPress site
- `WORDPRESS_DB_PASSWORD`: Password for the WordPress database

### Advanced Configuration
- `USE_RDS`: Set to "true" to use Amazon RDS instead of a local database
- `ENABLE_S3_MEDIA`: Set to "true" to store WordPress media on S3
- `ENABLE_AUTO_SCALING`: Set to "true" to enable auto scaling (high-availability only)

See `.env.example` for all available configuration options.

## 🔄 Workflow

1. Configure your settings in the `.env` file
2. Generate Terraform files with the generator
3. Navigate to the output directory
4. Run `terraform init` and `terraform apply`
5. Access your WordPress site at the provided URL

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

If you have any questions or need help, please open an issue on GitHub or contact the maintainers directly.
