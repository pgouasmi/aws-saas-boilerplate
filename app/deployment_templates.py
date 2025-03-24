# deployment_templates.py
"""
Définition des templates de déploiement qui spécifient quels composants
inclure pour chaque type de déploiement.
"""

DEPLOYMENT_TEMPLATES = {
    "cost-efficient": {
        "description": "Configuration économique avec une seule instance EC2 et un load balancer",
        "components": [
            "provider",
            "vpc",
            "internet_gateway",
            "subnet",
            "route_table",
            "security_group_instance",
            "security_group_lb",
            "ec2_instance",
            "load_balancer",
            "target_group"
        ],
        "variable_sections": [
            "aws", 
            "vpc", 
            "ec2", 
            "wordpress"
        ],
        "outputs": [
            "load_balancer_dns",
            "instance_ip"
        ]
    },
    "high-availability": {
        "description": "Configuration haute disponibilité avec multi-AZ, RDS et auto-scaling",
        "components": [
            "provider",
            "vpc",
            "internet_gateway",
            "subnet_multi_az",
            "route_table",
            "security_group_instance",
            "security_group_lb",
            "security_group_rds",
            "rds_instance",
            "auto_scaling_group",
            "launch_template",
            "load_balancer",
            "target_group"
        ],
        "variable_sections": [
            "aws", 
            "vpc", 
            "ec2", 
            "rds",
            "auto_scaling",
            "wordpress"
        ],
        "outputs": [
            "load_balancer_dns",
            "rds_endpoint"
        ]
    }
}