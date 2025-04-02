#!/usr/bin/env python3
"""
Script de génération de fichiers Terraform pour différents types de déploiement WordPress.
Ce script utilise une architecture modulaire pour assembler les configurations Terraform
à partir de composants réutilisables, en fonction du type de déploiement choisi.
"""

import os
import sys
import json
import shutil
import argparse
from datetime import datetime

# Import des templates modulaires
from terraform_templates import TERRAFORM_TEMPLATES  # Templates de composants
from variables_templates import VARIABLE_TEMPLATES   # Templates de variables
from deployment_templates import DEPLOYMENT_TEMPLATES  # Définitions des déploiements
# from user_data_template import USER_DATA_TEMPLATE
from env_parser import parse_env_file

# Configuration globale
ENV_FILE_DEFAULT = '.env'
DEFAULT_OUTPUT_DIR = 'terraform-output'

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def create_directory(dir_name):
    """Create a directory if it doesn't exist."""
    if os.path.exists(dir_name):
        overwrite = input(f"Directory '{dir_name}' already exists. Overwrite? (y/n): ")
        if overwrite.lower() == 'y':
            shutil.rmtree(dir_name)
        else:
            print("Operation cancelled.")
            return False
    
    os.makedirs(dir_name)
    return True

def format_env_vars_for_terraform(env_vars):
    """Format environment variables for use in Terraform templates."""
    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create a copy to avoid modifying the original
    formatted_vars = env_vars.copy()
    
    # Format lists for Terraform
    for key, value in formatted_vars.items():
        if isinstance(value, list):
            formatted_vars[key] = json.dumps(value)
    
    # Add date to env_vars for template formatting
    formatted_vars["date"] = current_date
    
    return formatted_vars

def generate_main_tf(deployment_type, env_vars_formatted):
    """Generate main.tf content by assembling components."""
    if deployment_type not in DEPLOYMENT_TEMPLATES:
        print(f"Error: Unknown deployment type '{deployment_type}'")
        return ""
    
    deployment_config = DEPLOYMENT_TEMPLATES[deployment_type]
    components = deployment_config.get("components", [])
    
    content = f"# Terraform configuration for WordPress - {deployment_type.replace('-', ' ').title()} Setup\n"
    content += f"# Generated on: {env_vars_formatted['date']}\n"
    content += f"# This file was assembled from modular components\n\n"
    
    # Add each component
    for component in components:
        print(f"current component: {component}")
        if component in TERRAFORM_TEMPLATES:
            try:
                # Utiliser string substitution au lieu de format() pour éviter les problèmes d'accolades
                component_content = TERRAFORM_TEMPLATES[component]
                
                # Remplacer manuellement les placeholders
                for key, value in env_vars_formatted.items():
                    placeholder = "{" + key + "}"
                    component_content = component_content.replace(placeholder, str(value))
                
                content += component_content + "\n\n"
            except Exception as e:
                print(f"Warning: Error processing component {component}: {e}")
                print("Skipping this component")
    
    # Add outputs similar to components
    content += "# Outputs\n"
    for output in deployment_config.get("outputs", []):
        if output in TERRAFORM_TEMPLATES.get("outputs", {}):
            try:
                output_content = TERRAFORM_TEMPLATES["outputs"][output]
                for key, value in env_vars_formatted.items():
                    placeholder = "{" + key + "}"
                    output_content = output_content.replace(placeholder, str(value))
                content += output_content + "\n"
            except Exception as e:
                print(f"Warning: Error processing output {output}: {e}")
    
    return content

def generate_variables_tf(deployment_type, env_vars_formatted):
    """Generate variables.tf content by assembling sections."""
    if deployment_type not in DEPLOYMENT_TEMPLATES:
        print(f"Error: Unknown deployment type '{deployment_type}'")
        return ""
    
    deployment_config = DEPLOYMENT_TEMPLATES[deployment_type]
    variable_sections = deployment_config.get("variable_sections", [])
    
    content = f"# Variables for WordPress - {deployment_type.replace('-', ' ').title()} Setup\n"
    content += f"# Generated on: {env_vars_formatted['date']}\n\n"
    
    # Add each variable section
    for section in variable_sections:
        if section in VARIABLE_TEMPLATES:
            try:
                # Utiliser le remplacement manuel de chaînes au lieu de format()
                section_content = VARIABLE_TEMPLATES[section]
                
                # Remplacer manuellement les placeholders
                for key, value in env_vars_formatted.items():
                    placeholder = "{" + key + "}"
                    section_content = section_content.replace(placeholder, str(value))
                
                content += section_content + "\n\n"
            except Exception as e:
                print(f"Warning: Error processing variables section {section}: {e}")
                print("Skipping this section")
    
    return content

def generate_terraform_tfvars(deployment_type, env_vars_formatted):
    """Generate terraform.tfvars content from environment variables."""
    content = f"# Terraform variable values for WordPress - {deployment_type.replace('-', ' ').title()} Setup\n"
    content += f"# Generated on: {env_vars_formatted['date']}\n"
    content += f"# These values are generated from your .env file\n\n"
    
    # AWS configuration
    content += "# AWS Configuration\n"
    content += f'aws_region         = "{env_vars_formatted["aws_region"]}"\n'
    if env_vars_formatted["aws_access_key_id"]:
        content += f'aws_access_key_id     = "{env_vars_formatted["aws_access_key_id"]}"\n'
    if env_vars_formatted["aws_secret_access_key"]:
        content += f'aws_secret_access_key     = "{env_vars_formatted["aws_secret_access_key"]}"\n'
    
    # Project configuration
    content += "\n# Project Configuration\n"
    content += f'project_name       = "{env_vars_formatted["project_name"]}"\n'
    content += f'environment        = "{env_vars_formatted["environment"]}"\n'
    
    # Network configuration
    content += "\n# Network Configuration\n"
    content += f'vpc_cidr           = "{env_vars_formatted["vpc_cidr"]}"\n'
    content += f'subnet_cidr        = "{env_vars_formatted["subnet_cidr"]}"\n'
    content += f'allowed_ssh_ips    = {env_vars_formatted["allowed_ssh_ips"]}\n'
    content += f'allowed_http_ips   = {env_vars_formatted["allowed_http_ips"]}\n'
    
    # EC2 configuration
    content += "\n# EC2 Configuration\n"
    content += f'instance_type      = "{env_vars_formatted["instance_type"]}"\n'
    content += f'instance_ami       = "{env_vars_formatted["instance_ami"]}"\n'
    content += f'instance_volume_size = {env_vars_formatted["instance_volume_size"]}\n'
    if env_vars_formatted["key_name"]:
        content += f'key_name           = "{env_vars_formatted["key_name"]}"\n'
    
    # WordPress configuration
    content += "\n# WordPress Configuration\n"
    content += f'wordpress_domain     = "{env_vars_formatted["wordpress_domain"]}"\n'
    content += f'wordpress_db_name    = "{env_vars_formatted["wordpress_db_name"]}"\n'
    content += f'wordpress_db_user    = "{env_vars_formatted["wordpress_db_user"]}"\n'
    content += f'wordpress_db_password = "{env_vars_formatted["wordpress_db_password"]}"\n'
    content += f'wordpress_site_title = "{env_vars_formatted["wordpress_site_title"]}"\n'
    content += f'wordpress_admin_user = "{env_vars_formatted["wordpress_admin_user"]}"\n'
    content += f'wordpress_admin_password = "{env_vars_formatted["wordpress_admin_password"]}"\n'
    content += f'wordpress_admin_email = "{env_vars_formatted["wordpress_admin_email"]}"\n'
    
    # Add advanced configuration if needed for this deployment type
    if deployment_type == "high-availability":
        content += "\n# High Availability Configuration\n"
        content += f'use_rds            = "{env_vars_formatted["use_rds"]}"\n'
        content += f'rds_instance_class = "{env_vars_formatted["rds_instance_class"]}"\n'
        content += f'rds_storage_size   = {env_vars_formatted["rds_storage_size"]}\n'
        content += f'rds_multi_az       = "{env_vars_formatted["rds_multi_az"]}"\n'
        content += f'enable_auto_scaling = "{env_vars_formatted["enable_auto_scaling"]}"\n'
        content += f'min_instances      = {env_vars_formatted["min_instances"]}\n'
        content += f'max_instances      = {env_vars_formatted["max_instances"]}\n'
        content += f'scale_up_cpu_threshold = {env_vars_formatted["scale_up_cpu_threshold"]}\n'
        content += f'scale_down_cpu_threshold = {env_vars_formatted["scale_down_cpu_threshold"]}\n'
    
    return content

def assemble_terraform_configs(deployment_type, env_vars):
    """
    Assemble Terraform configurations based on deployment type.
    Returns a dictionary with content for each file.
    """
    # Format environment variables for Terraform
    env_vars_formatted = format_env_vars_for_terraform(env_vars)
    
    # Generate configuration files
    main_tf = generate_main_tf(deployment_type, env_vars_formatted)
    variables_tf = generate_variables_tf(deployment_type, env_vars_formatted)
    terraform_tfvars = generate_terraform_tfvars(deployment_type, env_vars_formatted)
    
    return {
        "main.tf": main_tf,
        "variables.tf": variables_tf,
        "terraform.tfvars": terraform_tfvars
    }

def write_terraform_files(configs, directory):
    """Write Terraform configuration files to the specified directory."""
    for filename, content in configs.items():
        file_path = os.path.join(directory, filename)
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Created: {file_path}")
    return True

def write_env_file(env_vars, directory):
    """Write a copy of the .env file to the output directory."""
    env_file_path = os.path.join(directory, ".env")
    
    with open(env_file_path, 'w') as f:
        f.write("# WordPress Terraform Configuration\n")
        f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("#===========================================================\n")
        f.write("# AWS CONFIGURATION\n")
        f.write("#===========================================================\n")
        f.write(f"AWS_REGION={env_vars['aws_region']}\n")
        f.write(f"AWS_ACCESS_KEY_ID={env_vars['aws_access_key']}\n")
        f.write(f"AWS_SECRET_ACCESS_KEY={env_vars['aws_secret_key']}\n")
        
        f.write("\n#===========================================================\n")
        f.write("# NETWORK CONFIGURATION\n")
        f.write("#===========================================================\n")
        f.write(f"PROJECT_NAME={env_vars['project_name']}\n")
        f.write(f"ENVIRONMENT={env_vars['environment']}\n")
        f.write(f"CIDR_BLOCK={env_vars['vpc_cidr']}\n")
        f.write(f"SUBNET_CIDR_BLOCK={env_vars['subnet_cidr']}\n")
        
        # Continue with other sections...
        
    print(f"Created: {env_file_path}")
    return True

def generate_deployment(deployment_type, env_vars, directory=None):
    """Generate Terraform files for the specified deployment type."""
    # Default directory if not specified
    if not directory:
        directory = f"terraform-{deployment_type}"
        directory = input(f"Enter directory name for the Terraform files [{directory}]: ") or directory
    
    if not create_directory(directory):
        return False
    
    # Generate Terraform configurations
    configs = assemble_terraform_configs(deployment_type, env_vars)
    
    # Write configurations to files
    success = write_terraform_files(configs, directory)
    
    # Write a copy of the .env file
    # if success:
    #     write_env_file(env_vars, directory)
    
    if success:
        print(f"\nTerraform files for {deployment_type.replace('-', ' ').title()} deployment generated successfully!")
        print(f"\nTo deploy:")
        print(f"1. Navigate to the '{directory}' directory")
        print(f"2. Run 'terraform init'")
        print(f"3. Run 'terraform apply'")
    
    return success

def display_menu():
    """Display the main menu."""
    clear_screen()
    print("=" * 60)
    print("            WORDPRESS TERRAFORM GENERATOR")
    print("=" * 60)
    print("\nSelect the type of deployment you want to generate:")
    
    # Dynamically generate menu options from DEPLOYMENT_TEMPLATES
    i = 1
    deployment_options = {}
    for deployment_type, config in DEPLOYMENT_TEMPLATES.items():
        description = config.get("description", deployment_type.replace("-", " ").title())
        print(f"\n{i}. {description}")
        deployment_options[i] = deployment_type
        i += 1
    
    print("\n0. Exit")
    print("\n" + "=" * 60)
    
    return deployment_options

def get_menu_choice(max_choice):
    """Get the user's menu choice."""
    while True:
        try:
            choice = int(input(f"\nEnter your choice [0-{max_choice}]: "))
            if 0 <= choice <= max_choice:
                return choice
            print(f"Invalid choice. Please enter a number between 0 and {max_choice}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def show_env_vars_summary(env_vars):
    """Show a summary of the loaded environment variables."""
    print("\nConfiguration Summary:")
    print("=" * 60)
    print(f"AWS Region: {env_vars['aws_region']}")
    print(f"Project Name: {env_vars['project_name']}")
    print(f"WordPress Domain: {env_vars['wordpress_domain']}")
    print(f"Instance Type: {env_vars['instance_type']}")
    
    # Show advanced configuration if enabled
    if env_vars['use_rds'] == 'true':
        print(f"RDS: Enabled ({env_vars['rds_instance_class']})")
    if env_vars['enable_auto_scaling'] == 'true':
        print(f"Auto Scaling: Enabled ({env_vars['min_instances']}-{env_vars['max_instances']} instances)")
    if env_vars['enable_s3_media'] == 'true':
        print(f"S3 Media Storage: Enabled")
    
    print("=" * 60)
    print()

def interactive_mode(env_vars):
    """Run the script in interactive mode with a menu."""
    while True:
        deployment_options = display_menu()
        show_env_vars_summary(env_vars)
        choice = get_menu_choice(len(deployment_options))
        
        if choice == 0:
            print("\nExiting. Goodbye!")
            sys.exit(0)
        elif choice in deployment_options:
            deployment_type = deployment_options[choice]
            generate_deployment(deployment_type, env_vars)
            input("\nPress Enter to return to the main menu...")
        else:
            print("Invalid choice. Please try again.")

def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate Terraform files for WordPress deployment.')
    parser.add_argument('--env', '-e', default=ENV_FILE_DEFAULT, help=f'Path to .env file (default: {ENV_FILE_DEFAULT})')
    parser.add_argument('--type', '-t', choices=list(DEPLOYMENT_TEMPLATES.keys()), help='Deployment type')
    parser.add_argument('--output', '-o', help='Output directory')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode (default if no type is specified)')
    return parser.parse_args()

# def generate_user_data(env_vars):
#     """Génère le script user_data pour l'instance EC2 en remplaçant les variables."""
    
#     if "user_data" not in TERRAFORM_TEMPLATES:
#         print("Warning: user_data template not found, using empty script")
#         return ""
    
#     # Obtenez le template
#     user_data_template = TERRAFORM_TEMPLATES["user_data"]
    
#     # Remplacez les variables du template avec celles de env_vars
#     user_data_script = user_data_template
    
#     # Liste des variables à remplacer dans le script
#     variables_to_replace = [
#         "wordpress_domain", "wordpress_db_name", "wordpress_db_user", 
#         "wordpress_db_password", "wordpress_site_title", "wordpress_admin_user",
#         "wordpress_admin_password", "wordpress_admin_email"
#     ]
    
#     # Remplacer chaque occurrence
#     for var in variables_to_replace:
#         placeholder = "${" + var + "}"
#         replacement = str(env_vars.get(var, ""))
#         user_data_script = user_data_script.replace(placeholder, replacement)

#     print(f"\n\nUser data script:\n{user_data_script}\n\n")
    
#     env_vars["user_data_script"] = user_data_script

def main():
    """Main function to run the script."""
    args = parse_command_line_args()
    
    # Load environment variables
    env_vars = parse_env_file(args.env)

    # generate_user_data(env_vars)
    
    # Determine mode (interactive or direct)
    if args.type and not args.interactive:
        generate_deployment(args.type, env_vars, args.output)
    else:
        interactive_mode(env_vars)

if __name__ == "__main__":
    main()