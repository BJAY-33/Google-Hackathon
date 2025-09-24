"""
Script Tools - Tools for automation script generation and validation
"""

import os
import subprocess
import tempfile
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import re

class ScriptTemplate(BaseModel):
    """Model for script template information."""
    script_type: str
    language: str
    template: str
    description: str
    dependencies: List[str] = Field(default_factory=list)

class GeneratedScript(BaseModel):
    """Model for generated script information."""
    script_id: str
    title: str
    language: str
    content: str
    description: str
    usage_instructions: str
    dependencies: List[str] = Field(default_factory=list)

def generate_automation_script(script_requirements: str, script_type: str = "general", language: str = "python") -> Dict[str, Any]:
    """
    Generate automation scripts based on requirements.
    
    Args:
        script_requirements: Description of what the script should do
        script_type: Type of script (ci_cd, deployment, testing, data_processing, etc.)
        language: Programming language for the script
        
    Returns:
        Dictionary with generated script content
    """
    try:
        # Script templates for different types and languages
        script_templates = {
            "ci_cd": {
                "python": {
                    "template": """#!/usr/bin/env python3
\"\"\"
CI/CD Automation Script
{description}
\"\"\"

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CICDPipeline:
    def __init__(self):
        self.project_root = Path.cwd()
        self.build_dir = self.project_root / "build"
        self.test_results_dir = self.project_root / "test-results"
    
    def setup_environment(self):
        \"\"\"Set up the build environment.\"\"\"
        logger.info("Setting up build environment...")
        self.build_dir.mkdir(exist_ok=True)
        self.test_results_dir.mkdir(exist_ok=True)
        
        # Install dependencies
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
            logger.info("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {{e}}")
            sys.exit(1)
    
    def run_tests(self):
        \"\"\"Run the test suite.\"\"\"
        logger.info("Running test suite...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "--junitxml=test-results/junit.xml",
                "--cov=src",
                "--cov-report=html:test-results/coverage"
            ], check=True, capture_output=True, text=True)
            logger.info("Tests passed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Tests failed: {{e.stdout}}\\n{{e.stderr}}")
            return False
    
    def build_application(self):
        \"\"\"Build the application.\"\"\"
        logger.info("Building application...")
        try:
            # Add your build commands here
            subprocess.run(["python", "setup.py", "build"], check=True)
            logger.info("Application built successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Build failed: {{e}}")
            return False
    
    def deploy(self):
        \"\"\"Deploy the application.\"\"\"
        logger.info("Deploying application...")
        # Add deployment logic here
        logger.info("Deployment completed")
    
    def run_pipeline(self):
        \"\"\"Run the complete CI/CD pipeline.\"\"\"
        logger.info("Starting CI/CD pipeline...")
        
        self.setup_environment()
        
        if not self.run_tests():
            logger.error("Pipeline failed: Tests did not pass")
            sys.exit(1)
        
        if not self.build_application():
            logger.error("Pipeline failed: Build failed")
            sys.exit(1)
        
        self.deploy()
        logger.info("CI/CD pipeline completed successfully")

if __name__ == "__main__":
    pipeline = CICDPipeline()
    pipeline.run_pipeline()
""",
                    "description": "CI/CD automation script with testing, building, and deployment steps",
                    "dependencies": ["pytest", "coverage"]
                },
                "bash": {
                    "template": """#!/bin/bash
# CI/CD Automation Script
# {description}

set -e  # Exit on any error

# Configuration
PROJECT_ROOT=$(pwd)
BUILD_DIR="$PROJECT_ROOT/build"
TEST_RESULTS_DIR="$PROJECT_ROOT/test-results"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

log_info() {{
    echo -e "${{GREEN}}[INFO]${{NC}} $1"
}}

log_error() {{
    echo -e "${{RED}}[ERROR]${{NC}} $1"
}}

log_warning() {{
    echo -e "${{YELLOW}}[WARNING]${{NC}} $1"
}}

setup_environment() {{
    log_info "Setting up build environment..."
    mkdir -p "$BUILD_DIR"
    mkdir -p "$TEST_RESULTS_DIR"
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    log_info "Environment setup completed"
}}

run_tests() {{
    log_info "Running test suite..."
    
    if command -v pytest &> /dev/null; then
        pytest --junitxml="$TEST_RESULTS_DIR/junit.xml" --cov=src --cov-report=html:"$TEST_RESULTS_DIR/coverage"
    else
        log_warning "pytest not found, skipping tests"
        return 0
    fi
    
    log_info "Tests completed successfully"
}}

build_application() {{
    log_info "Building application..."
    
    # Add your build commands here
    # Example: python setup.py build
    
    log_info "Application built successfully"
}}

deploy() {{
    log_info "Deploying application..."
    
    # Add deployment logic here
    
    log_info "Deployment completed"
}}

main() {{
    log_info "Starting CI/CD pipeline..."
    
    setup_environment
    run_tests
    build_application
    deploy
    
    log_info "CI/CD pipeline completed successfully"
}}

# Run main function
main "$@"
""",
                    "description": "Bash CI/CD automation script",
                    "dependencies": []
                }
            },
            "deployment": {
                "python": {
                    "template": """#!/usr/bin/env python3
\"\"\"
Deployment Automation Script
{description}
\"\"\"

import os
import sys
import subprocess
import logging
import json
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentManager:
    def __init__(self, config_file="deployment.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        \"\"\"Load deployment configuration.\"\"\"
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return {{
                "environment": "production",
                "app_name": "my-app",
                "docker_image": "my-app:latest",
                "replicas": 3,
                "health_check_url": "/health"
            }}
    
    def build_docker_image(self):
        \"\"\"Build Docker image.\"\"\"
        logger.info("Building Docker image...")
        try:
            subprocess.run([
                "docker", "build", 
                "-t", self.config["docker_image"], 
                "."
            ], check=True)
            logger.info("Docker image built successfully")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to build Docker image: {{e}}")
            sys.exit(1)
    
    def deploy_to_kubernetes(self):
        \"\"\"Deploy to Kubernetes cluster.\"\"\"
        logger.info("Deploying to Kubernetes...")
        try:
            # Apply Kubernetes manifests
            subprocess.run(["kubectl", "apply", "-f", "k8s/"], check=True)
            
            # Wait for rollout
            subprocess.run([
                "kubectl", "rollout", "status", 
                f"deployment/{{self.config['app_name']}}"
            ], check=True)
            
            logger.info("Kubernetes deployment successful")
        except subprocess.CalledProcessError as e:
            logger.error(f"Kubernetes deployment failed: {{e}}")
            sys.exit(1)
    
    def health_check(self):
        \"\"\"Perform health check after deployment.\"\"\"
        logger.info("Performing health check...")
        # Add health check logic here
        time.sleep(10)  # Wait for services to start
        logger.info("Health check passed")
    
    def deploy(self):
        \"\"\"Execute deployment process.\"\"\"
        logger.info(f"Starting deployment to {{self.config['environment']}}...")
        
        self.build_docker_image()
        self.deploy_to_kubernetes()
        self.health_check()
        
        logger.info("Deployment completed successfully")

if __name__ == "__main__":
    deployer = DeploymentManager()
    deployer.deploy()
""",
                    "description": "Docker and Kubernetes deployment automation script",
                    "dependencies": ["docker", "kubectl"]
                }
            },
            "testing": {
                "python": {
                    "template": """#!/usr/bin/env python3
\"\"\"
Test Automation Script
{description}
\"\"\"

import os
import sys
import subprocess
import logging
import json
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestRunner:
    def __init__(self):
        self.project_root = Path.cwd()
        self.test_results_dir = self.project_root / "test-results"
        self.test_results_dir.mkdir(exist_ok=True)
    
    def run_unit_tests(self):
        \"\"\"Run unit tests.\"\"\"
        logger.info("Running unit tests...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/unit/",
                "--junitxml=test-results/unit-tests.xml",
                "--cov=src",
                "--cov-report=html:test-results/unit-coverage",
                "-v"
            ], check=True, capture_output=True, text=True)
            logger.info("Unit tests passed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Unit tests failed: {{e.stdout}}\\n{{e.stderr}}")
            return False
    
    def run_integration_tests(self):
        \"\"\"Run integration tests.\"\"\"
        logger.info("Running integration tests...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/integration/",
                "--junitxml=test-results/integration-tests.xml",
                "-v"
            ], check=True, capture_output=True, text=True)
            logger.info("Integration tests passed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Integration tests failed: {{e.stdout}}\\n{{e.stderr}}")
            return False
    
    def run_e2e_tests(self):
        \"\"\"Run end-to-end tests.\"\"\"
        logger.info("Running end-to-end tests...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/e2e/",
                "--junitxml=test-results/e2e-tests.xml",
                "-v"
            ], check=True, capture_output=True, text=True)
            logger.info("End-to-end tests passed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"End-to-end tests failed: {{e.stdout}}\\n{{e.stderr}}")
            return False
    
    def generate_report(self):
        \"\"\"Generate test report.\"\"\"
        logger.info("Generating test report...")
        
        report = {{
            "timestamp": datetime.now().isoformat(),
            "test_results": {{
                "unit_tests": "passed",
                "integration_tests": "passed", 
                "e2e_tests": "passed"
            }}
        }}
        
        with open(self.test_results_dir / "test-report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info("Test report generated")
    
    def run_all_tests(self):
        \"\"\"Run all test suites.\"\"\"
        logger.info("Starting comprehensive test run...")
        
        results = []
        results.append(self.run_unit_tests())
        results.append(self.run_integration_tests())
        results.append(self.run_e2e_tests())
        
        if all(results):
            logger.info("All tests passed successfully")
            self.generate_report()
            return True
        else:
            logger.error("Some tests failed")
            return False

if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
""",
                    "description": "Comprehensive test automation script with unit, integration, and E2E tests",
                    "dependencies": ["pytest", "pytest-cov"]
                }
            },
            "data_processing": {
                "python": {
                    "template": """#!/usr/bin/env python3
\"\"\"
Data Processing Automation Script
{description}
\"\"\"

import os
import sys
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    def __init__(self, input_dir="data/input", output_dir="data/output"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_data(self, filename):
        \"\"\"Load data from various formats.\"\"\"
        file_path = self.input_dir / filename
        
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {{file_path}}")
        
        if filename.endswith('.csv'):
            return pd.read_csv(file_path)
        elif filename.endswith('.json'):
            return pd.read_json(file_path)
        elif filename.endswith('.xlsx'):
            return pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {{filename}}")
    
    def clean_data(self, df):
        \"\"\"Clean and preprocess data.\"\"\"
        logger.info("Cleaning data...")
        
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df = df.fillna(method='forward')
        
        # Add processing timestamp
        df['processed_at'] = datetime.now()
        
        logger.info(f"Data cleaned. Shape: {{df.shape}}")
        return df
    
    def transform_data(self, df):
        \"\"\"Transform data according to business rules.\"\"\"
        logger.info("Transforming data...")
        
        # Add your transformation logic here
        # Example: df['new_column'] = df['existing_column'] * 2
        
        logger.info("Data transformation completed")
        return df
    
    def save_data(self, df, filename):
        \"\"\"Save processed data.\"\"\"
        output_path = self.output_dir / filename
        
        if filename.endswith('.csv'):
            df.to_csv(output_path, index=False)
        elif filename.endswith('.json'):
            df.to_json(output_path, orient='records', indent=2)
        elif filename.endswith('.xlsx'):
            df.to_excel(output_path, index=False)
        
        logger.info(f"Data saved to {{output_path}}")
    
    def generate_summary(self, df):
        \"\"\"Generate data processing summary.\"\"\"
        summary = {{
            "timestamp": datetime.now().isoformat(),
            "records_processed": len(df),
            "columns": list(df.columns),
            "data_types": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict()
        }}
        
        summary_path = self.output_dir / "processing_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Summary saved to {{summary_path}}")
    
    def process_file(self, input_filename, output_filename):
        \"\"\"Process a single file.\"\"\"
        logger.info(f"Processing {{input_filename}}...")
        
        # Load data
        df = self.load_data(input_filename)
        
        # Clean data
        df = self.clean_data(df)
        
        # Transform data
        df = self.transform_data(df)
        
        # Save processed data
        self.save_data(df, output_filename)
        
        # Generate summary
        self.generate_summary(df)
        
        logger.info("Processing completed successfully")

if __name__ == "__main__":
    processor = DataProcessor()
    
    # Example usage
    processor.process_file("input_data.csv", "processed_data.csv")
""",
                    "description": "Data processing automation script with cleaning, transformation, and reporting",
                    "dependencies": ["pandas", "openpyxl"]
                }
            }
        }
        
        # Determine script content based on type and language
        if script_type in script_templates and language in script_templates[script_type]:
            template_data = script_templates[script_type][language]
            script_content = template_data["template"].format(description=script_requirements)
            dependencies = template_data["dependencies"]
            description = template_data["description"]
        else:
            # Generate a generic script
            script_content = f"""#!/usr/bin/env python3
\"\"\"
{script_requirements}
\"\"\"

import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    \"\"\"Main function for the automation script.\"\"\"
    logger.info("Starting automation script...")
    
    # Add your automation logic here
    # Based on requirements: {script_requirements}
    
    logger.info("Automation script completed successfully")

if __name__ == "__main__":
    main()
"""
            dependencies = []
            description = f"Generated automation script: {script_requirements}"
        
        # Generate usage instructions
        usage_instructions = f"""
Usage Instructions:
1. Make the script executable: chmod +x script.{language}
2. Install dependencies: pip install {' '.join(dependencies) if dependencies else 'No dependencies required'}
3. Run the script: python script.{language}

Requirements addressed:
{script_requirements}

Dependencies:
{', '.join(dependencies) if dependencies else 'None'}
"""
        
        return {
            "status": "success",
            "message": f"Generated {script_type} automation script in {language}",
            "script": {
                "script_id": f"AUTO-{script_type.upper()}-001",
                "title": f"{script_type.title()} Automation Script",
                "language": language,
                "content": script_content,
                "description": description,
                "usage_instructions": usage_instructions,
                "dependencies": dependencies,
                "script_type": script_type
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating automation script: {str(e)}",
            "script": None
        }

def validate_script_syntax(script_content: str, language: str = "python") -> Dict[str, Any]:
    """
    Validate script syntax and check for common issues.
    
    Args:
        script_content: The script content to validate
        language: Programming language of the script
        
    Returns:
        Dictionary with validation results
    """
    try:
        validation_results = {
            "syntax_valid": True,
            "issues": [],
            "warnings": [],
            "suggestions": []
        }
        
        if language.lower() == "python":
            # Check Python syntax
            try:
                compile(script_content, '<string>', 'exec')
                validation_results["syntax_valid"] = True
            except SyntaxError as e:
                validation_results["syntax_valid"] = False
                validation_results["issues"].append(f"Syntax error at line {e.lineno}: {e.msg}")
            
            # Check for common issues
            lines = script_content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Check for missing imports
                if 'subprocess.run' in line and 'import subprocess' not in script_content:
                    validation_results["warnings"].append(f"Line {i}: subprocess used but not imported")
                
                if 'logging.' in line and 'import logging' not in script_content:
                    validation_results["warnings"].append(f"Line {i}: logging used but not imported")
                
                # Check for security issues
                if 'shell=True' in line:
                    validation_results["warnings"].append(f"Line {i}: shell=True can be a security risk")
                
                if 'os.system(' in line:
                    validation_results["warnings"].append(f"Line {i}: os.system() can be a security risk, consider subprocess")
                
                # Check for best practices
                if line.strip().startswith('print(') and 'logger' in script_content:
                    validation_results["suggestions"].append(f"Line {i}: Consider using logger instead of print")
        
        elif language.lower() == "bash":
            # Basic bash validation
            if not script_content.strip().startswith('#!/bin/bash'):
                validation_results["warnings"].append("Missing shebang line")
            
            if 'set -e' not in script_content:
                validation_results["suggestions"].append("Consider adding 'set -e' for better error handling")
        
        return {
            "status": "success",
            "message": "Script validation completed",
            "validation": validation_results
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error validating script: {str(e)}",
            "validation": {"syntax_valid": False, "issues": [str(e)]}
        }

def create_deployment_script(deployment_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create deployment-specific automation scripts.
    
    Args:
        deployment_config: Configuration for deployment (platform, environment, etc.)
        
    Returns:
        Dictionary with generated deployment script
    """
    try:
        platform = deployment_config.get("platform", "docker")
        environment = deployment_config.get("environment", "production")
        app_name = deployment_config.get("app_name", "my-app")
        
        if platform.lower() == "docker":
            script_content = f"""#!/bin/bash
# Docker Deployment Script for {app_name}
# Environment: {environment}

set -e

APP_NAME="{app_name}"
ENVIRONMENT="{environment}"
DOCKER_IMAGE="$APP_NAME:latest"
CONTAINER_NAME="$APP_NAME-$ENVIRONMENT"

echo "Starting deployment of $APP_NAME to $ENVIRONMENT..."

# Build Docker image
echo "Building Docker image..."
docker build -t $DOCKER_IMAGE .

# Stop existing container
echo "Stopping existing container..."
docker stop $CONTAINER_NAME || true
docker rm $CONTAINER_NAME || true

# Run new container
echo "Starting new container..."
docker run -d \\
    --name $CONTAINER_NAME \\
    --restart unless-stopped \\
    -p 8080:8080 \\
    $DOCKER_IMAGE

# Health check
echo "Performing health check..."
sleep 10
if curl -f http://localhost:8080/health; then
    echo "Deployment successful!"
else
    echo "Health check failed!"
    exit 1
fi

echo "Deployment completed successfully"
"""
        
        elif platform.lower() == "kubernetes":
            script_content = f"""#!/bin/bash
# Kubernetes Deployment Script for {app_name}
# Environment: {environment}

set -e

APP_NAME="{app_name}"
ENVIRONMENT="{environment}"
NAMESPACE="$APP_NAME-$ENVIRONMENT"

echo "Starting Kubernetes deployment of $APP_NAME to $ENVIRONMENT..."

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Apply Kubernetes manifests
echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/ -n $NAMESPACE

# Wait for deployment to complete
echo "Waiting for deployment to complete..."
kubectl rollout status deployment/$APP_NAME -n $NAMESPACE --timeout=300s

# Verify deployment
echo "Verifying deployment..."
kubectl get pods -n $NAMESPACE

echo "Kubernetes deployment completed successfully"
"""
        
        else:
            script_content = f"""#!/bin/bash
# Generic Deployment Script for {app_name}
# Environment: {environment}

set -e

APP_NAME="{app_name}"
ENVIRONMENT="{environment}"

echo "Starting deployment of $APP_NAME to $ENVIRONMENT..."

# Add your deployment logic here
echo "Deployment logic not implemented for platform: {platform}"

echo "Deployment completed"
"""
        
        return {
            "status": "success",
            "message": f"Generated {platform} deployment script",
            "script": {
                "script_id": f"DEPLOY-{platform.upper()}-001",
                "title": f"{platform.title()} Deployment Script",
                "language": "bash",
                "content": script_content,
                "description": f"Deployment automation for {app_name} on {platform}",
                "usage_instructions": f"""
Usage:
1. Make executable: chmod +x deploy.sh
2. Run: ./deploy.sh
3. Monitor logs for deployment status

Configuration:
- App Name: {app_name}
- Environment: {environment}
- Platform: {platform}
""",
                "dependencies": [platform] if platform in ["docker", "kubectl"] else [],
                "platform": platform,
                "environment": environment
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating deployment script: {str(e)}",
            "script": None
        }
