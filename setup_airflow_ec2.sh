#!/bin/bash

# Update EC2 instance
sudo yum update -y  # Using yum for Amazon Linux instead of apt

# Install Python inside EC2 instance
sudo yum install python3 -y  # Install Python 3

# Install pip for Python package management
sudo yum install python3-pip -y

# Install Python virtual environment package
sudo yum install python3-venv -y

# Create Python virtual environment for Airflow
python3 -m venv airflow_env

# Activate the Python virtual environment
source airflow_env/bin/activate

# Install necessary Python packages
pip install pandas
pip install apache-airflow
pip install requests
pip install boto3

# Configure Airflow (Initialize Airflow database)
airflow db init

# Start Airflow standalone mode for initial setup
airflow standalone

# Start Airflow webserver
airflow webserver --port 8080

# Start Airflow scheduler (in another terminal or SSH session)
airflow scheduler

# Ensure EC2 instance's firewall allows access to port 8080
sudo ufw allow 8080/tcp

