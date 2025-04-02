# Makefile for WordPress Terraform Deployment Project
# Structure:
# - .env (root directory)
# - app/ (contains Python scripts)
# - wordpress-install/ (contains WordPress installation scripts)

# Default target
.PHONY: all
all: help

# Variables
PYTHON = python3
PIP = pip3
ENV_FILE = .env
TF_DIR = terraform-output
PYTHON_SCRIPT = app/app.py
INSTALL_DIR = wordpress-install
INSTALL_SCRIPT = $(INSTALL_DIR)/wordpress-setup.sh

create-venv:
	@if [ ! -d venv]; then \
		python3 -m venv venv; \
		echo "Created venv!\n"; \
	else \
		echo "Venv already created!"; \
	fi


activate-venv:
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		echo "Venv already Activated!"; \
	else \
		source venv/bin/activate; \
		echo "Activated venv!\n"; \
	fi

install-deps:
	pip install -r requirements.txt

setup-venv: create-venv activate-venv install-deps

# Check if .env file exists
env-check:
	@if [ ! -f $(ENV_FILE) ]; then \
		echo "$(ENV_FILE) file not found. Creating a template..."; \
		cp $(ENV_FILE).example $(ENV_FILE) 2>/dev/null || echo "# WordPress Terraform Configuration\n\n# AWS Configuration\nAWS_REGION=us-east-1\n\n# WordPress Configuration\nWORDPRESS_DOMAIN=example.com\nWORDPRESS_DB_NAME=wordpress\n" > $(ENV_FILE); \
		echo "Please edit $(ENV_FILE) with your configuration values."; \
		exit 1; \
	fi

# Create directory if it doesn't exist
define ensure_dir
	@mkdir -p $(1)
endef

# Install dependencies
.PHONY: deps
deps:
	$(call ensure_dir,app)
	$(call ensure_dir,$(INSTALL_DIR))
	$(PIP) install -r requirements.txt

# Generate terraform files
.PHONY: generate
generate: env-check
	$(PYTHON) $(PYTHON_SCRIPT)

# Generate cost-efficient deployment
.PHONY: cost-efficient
cost-efficient: env-check
	@echo "Generating cost-efficient deployment..."
	@mkdir -p $(TF_DIR)
	$(PYTHON) $(PYTHON_SCRIPT) --type cost-efficient --output $(TF_DIR) --env $(ENV_FILE)
	@echo "Files generated in $(TF_DIR)/"

# Generate high-availability deployment (placeholder)
.PHONY: high-availability
high-availability: env-check
	@echo "Generating high-availability deployment..."
	@mkdir -p $(TF_DIR)-ha
	$(PYTHON) $(PYTHON_SCRIPT) --type high-availability --output $(TF_DIR)-ha --env $(ENV_FILE)
	@echo "Files generated in $(TF_DIR)-ha/"

# Run Terraform actions
.PHONY: tf-init
tf-init:
	@if [ ! -d $(TF_DIR) ]; then \
		echo "Terraform directory not found. Run 'make generate' first."; \
		exit 1; \
	fi
	cd $(TF_DIR) && terraform init

.PHONY: tf-plan
tf-plan: tf-init
	cd $(TF_DIR) && terraform plan

.PHONY: tf-apply
tf-apply: tf-init
	cd $(TF_DIR) && terraform apply

.PHONY: tf-destroy
tf-destroy: tf-init
	cd $(TF_DIR) && terraform destroy

# Test installation script locally
.PHONY: test-install
test-install: env-check
	@echo "Testing WordPress installation script..."
	@if [ ! -f $(INSTALL_SCRIPT) ]; then \
		echo "Installation script not found at $(INSTALL_SCRIPT)"; \
		exit 1; \
	fi
	chmod +x $(INSTALL_SCRIPT)
	# This will just validate the script syntax without running it
	bash -n $(INSTALL_SCRIPT)
	@echo "Installation script syntax is valid."

# Upload installation script to a web server (example with AWS S3)
.PHONY: upload-script
upload-script: test-install
	@if [ -z "$$S3_BUCKET" ]; then \
		echo "Please set S3_BUCKET environment variable"; \
		exit 1; \
	fi
	aws s3 cp $(INSTALL_SCRIPT) s3://$$S3_BUCKET/wordpress-setup.sh --acl public-read
	@echo "Script uploaded to s3://$$S3_BUCKET/wordpress-setup.sh"
	@echo "Public URL: https://$$S3_BUCKET.s3.amazonaws.com/wordpress-setup.sh"
	@echo "Update your .env file with WORDPRESS_SETUP_SCRIPT_URL=https://$$S3_BUCKET.s3.amazonaws.com/wordpress-setup.sh"

# Clean generated files
.PHONY: clean
clean:
	@echo "Cleaning generated files..."
	rm -rf $(TF_DIR) $(TF_DIR)-ha
	@echo "Cleaned."

# Deep clean (generated files and Python cache)
.PHONY: clean-all
clean-all: clean
	@echo "Removing Python cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "All cleaned."

re: clean cost-efficient

# Help information
.PHONY: help
help:
	@echo "WordPress Terraform Deployment - Makefile Help"
	@echo "=============================================="
	@echo ""
	@echo "Available commands:"
	@echo ""
	@echo "  make deps              - Install dependencies"
	@echo "  make generate          - Run the generator script interactively"
	@echo "  make cost-efficient    - Generate cost-efficient deployment"
	@echo "  make high-availability - Generate high-availability deployment"
	@echo "  make tf-init           - Initialize Terraform"
	@echo "  make tf-plan           - Plan Terraform deployment"
	@echo "  make tf-apply          - Apply Terraform deployment"
	@echo "  make tf-destroy        - Destroy Terraform resources"
	@echo "  make test-install      - Test WordPress installation script"
	@echo "  make upload-script     - Upload script to S3 (set S3_BUCKET env var)"
	@echo "  make clean             - Remove generated files"
	@echo "  make clean-all         - Remove all generated files and caches"
	@echo "  make help              - Show this help message"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Python 3"
	@echo "  - pip3"
	@echo "  - Terraform CLI"
	@echo "  - AWS CLI (for script upload)"
	@echo ""
	@echo "Configuration:"
	@echo "  Edit .env file in the root directory"