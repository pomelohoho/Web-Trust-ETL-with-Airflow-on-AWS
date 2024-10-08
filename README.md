# Web of Trust (WOT) API ETL Pipeline using Airflow on AWS

This project demonstrates how to build, deploy, and automate an ETL (Extract, Transform, Load) pipeline using Python and Apache Airflow on an AWS EC2 instance. The pipeline interacts with the **Web of Trust (WOT)** API to retrieve reputation data for websites, processes the data, and stores it in AWS S3 for future use.

## Project Overview

The goal of this project is to develop a scalable data pipeline that connects to the WOT API, retrieves website reputation data, processes the results, and loads the final dataset into AWS S3. The entire process is automated using Apache Airflow, enabling periodic data extraction and transformation.

## Project Objectives

1. **Data extraction**: Set up an extraction process to pull website reputation data from the **WOT API**.
2. **Data transformation**: Process the raw API data, converting it into a structured format such as CSV.
3. **Data storage**: Store the processed data in an AWS S3 bucket for further analysis and use.
4. **Pipeline automation**: Schedule and automate the entire process using Apache Airflow, ensuring that data is updated periodically.
5. **Scalability and extensibility**: Design the pipeline to scale, adding more data sources or expanding the WOT API queries as needed.

## Tools & Technologies

1. **Apache Airflow**: An open-source orchestration tool that helps manage, schedule, and monitor data workflows.
2. **AWS EC2**: Elastic Compute Cloud (EC2) is used to run the Airflow server and pipeline. It provides scalable compute capacity in the cloud.
3. **AWS S3**: Simple Storage Service (S3) is utilized to store the processed data in CSV format.
4. **Python**: Used for scripting and data transformation, with key libraries like `requests` for API calls and `pandas` for data manipulation.
5. **WOT API**: The Web of Trust API provides website reputation data, including safety and trustworthiness metrics.

## Pipeline Architecture

The architecture consists of several components that work together to automate the data pipeline, including:

- **Data Ingestion**: API requests are made to the WOT API using Airflow’s `SimpleHttpOperator` to retrieve reputation data for specified websites.
- **Data Transformation**: Python scripts process the API's JSON response, transforming the data into a structured format like CSV using `pandas`.
- **Data Storage**: The processed data is uploaded and stored in AWS S3 buckets.
- **Automation**: Airflow schedules and automates the ETL process, triggering it at regular intervals or based on specific conditions.

## Workflow Overview

1. **Data extraction**: 
   - The pipeline sends API requests to the **WOT API**, retrieving website safety, child safety, and trustworthiness information.
   - The `SimpleHttpOperator` in Airflow is used to handle the HTTP requests and responses, enabling a seamless connection between Airflow and the WOT API.

2. **Data transformation**:
   - Once the data is fetched from the API, it is processed using Python’s `pandas` library to transform the JSON structure into a tabular format (CSV).
   - Additional steps may include filtering, cleaning, and enriching the data before saving it.

3. **Data storage**:
   - After the transformation step, the processed data is saved into AWS S3 buckets in CSV format. AWS S3 provides highly available and durable cloud storage, ensuring the processed data is securely stored and easily accessible.

4. **Automation**:
   - The entire pipeline is automated using Airflow. Airflow triggers the API calls and subsequent processing steps based on a schedule or events.
   - Users can monitor the pipeline's performance and status through the Airflow web interface.

## Dataset: WOT API Data

The WOT API provides a reputation score and categories for websites, along with safety ratings. A sample response for a website like `facebook.com` looks like this:

```json
[
    {
        "target": "facebook.com",
        "safety": {
            "status": "SAFE",
            "reputations": 85,
            "confidence": 90
        },
        "childSafety": {
            "reputations": 75,
            "confidence": 80
        },
        "categories": [
            {
                "id": 104,
                "name": "social media",
                "confidence": 90
            }
        ]
    }
]
```

The following data points are extracted and processed:

- **Safety Status**: Whether the website is considered safe, unsafe, or suspicious.
- **Reputation Scores**: Reputation scores for general safety and child safety, ranging from 0 to 100.
- **Category Information**: Categories associated with the website, such as "phishing" or "social media".
You're right! The Airflow UI needs to be set up first before defining the DAGs, and the scheduling part is key in setting up the automation. Here's the revised step-by-step process with the correct order, including Airflow scheduling.

---

## Step-by-Step Implementation

### Step 1: Set up EC2 and install dependencies

1. **Launch an EC2 instance** on AWS, configure security group settings to allow SSH (port 22) and Airflow (port 8080) access.
2. **Install Python and Airflow** on the EC2 instance.
3. **Set up a Python virtual environment** to isolate dependencies. Install required libraries like `requests`, `pandas`, and `boto3`.

```bash
# Update the system and install Python
sudo yum update -y
sudo yum install python3

# Install virtual environment and Airflow
python3 -m venv airflow_env
source airflow_env/bin/activate

# Install Apache Airflow and other dependencies
pip install apache-airflow pandas requests boto3
```
<p align="center">
  <img width="1000" height="550" src="Images/ec2-amazon-linux.png">
  <h6 align = "center" > Source: Pom </h6>
</p>

### Step 2: Start Airflow Webserver and Scheduler

1. **Initialize Airflow** database and start the webserver:

```bash
# Initialize Airflow database
airflow db init

# Start Airflow webserver
airflow webserver --port 8080
```
<p align="center">
  <img width="1000" height="550" src="Images/airflow-ui.png">
  <h6 align = "center" > Source: Pom </h6>
</p>

2. **Start the Airflow scheduler** to enable the scheduling of DAGs:

```bash
airflow scheduler
```

3. **Access the Airflow UI** by opening a web browser and navigating to `http://<your-ec2-public-ip>:8080`. Make sure port 8080 is open in your EC2 security group to allow access.

### Step 3: Configure Airflow HTTP Connection to WOT API

In the Airflow UI:
- Navigate to **Admin > Connections**.
- Add a new connection:
  - **Conn ID**: `wot_api_conn`
  - **Conn Type**: HTTP
  - **Host**: `https://scorecard.api.mywot.com`
  - Leave other fields empty, as authentication will be provided in the DAG.
    
### Step 4: Store API Key in Airflow Variable**
For better security and flexibility, store the WOT API key in Airflow’s Variables so that the API key can be dynamically accessed in your DAG code without hardcoding it:

In the Airflow UI, go to Admin > Variables.
Create a new variable:
Key: wot_api_key
Value: <your_api_key>

### Step 5: Create the Airflow DAG

Store the 
The DAG (Directed Acyclic Graph) defines the workflow. The DAG fetches data from the WOT API, processes it, and stores the result in AWS S3.

Example DAG:

```python
from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python_operator import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
import pandas as pd
import json
import boto3

# Default args for the Airflow DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
with DAG(
    "wot_api_dag",
    default_args=default_args,
    schedule_interval="@daily",  # Schedule to run once a day
    catchup=False,
) as dag:

    # Python function to process the WOT API data
    def process_wot_data(**kwargs):

        # Transform the JSON response into a DataFrame
        # ...
       
        # Upload the file to AWS S3
        # ...
       
    # Task 1: Fetch data from the WOT API
    fetch_wot_data = SimpleHttpOperator(
        task_id="fetch_wot_data",
        http_conn_id="wot_api_conn",  # Airflow connection ID
        endpoint="v3/targets?t=facebook.com&t=google.com",  
        headers={
            "x-user-id": "9027864",  
            "x-api-key": Variable.get("wot_api_key") 
        },
        response_filter=lambda response: json.loads(response.text),
        log_response=True
    )

    # Task 2: Process and store the data in AWS S3
    process_data = PythonOperator(
        task_id="process_wot_data",
        python_callable=process_wot_data,
        provide_context=True
    )

    # Define task order
    fetch_wot_data >> process_data
```

### Step 6: Automate and Schedule the Pipeline

- The Airflow scheduler will automatically trigger the DAG based on the defined schedule (`@daily` in this case).
- You can monitor DAG runs, view logs, and see task progress in the Airflow UI under the **DAGs** section.

### Step 7: Store data in AWS S3

Processed data is uploaded to AWS S3 for persistent storage:

```python
import boto3
s3 = boto3.client('s3')
s3.upload_file('/tmp/data.csv', 'your-s3-bucket', 'path/to/data.csv')
```

## Conclusion

This project demonstrates how to build a scalable and automated ETL pipeline that fetches website reputation data from the **WOT API**, processes it, and stores the results in AWS S3. By leveraging Apache Airflow, the pipeline can be easily monitored, maintained, and extended to include more data sources or complex transformations.

### Discussion:
Why use the tools in this project: 

- **AWS EC2**: EC2 provides the computing infrastructure necessary to run the entire Airflow environment and handle the execution of Python scripts for data extraction and transformation. EC2's flexibility allows for the easy scaling of resources to accommodate varying workloads, such as increasing the number of websites queried from the WOT API. This makes it an ideal solution for running automated and resource-intensive tasks like ETL pipelines in the cloud.

- **AWS S3**: As a scalable and secure storage solution, AWS S3 is perfect for long-term storage of processed data. In this project, the reputation data collected from the WOT API is stored in S3 in a structured format (e.g., CSV). This enables easy integration with other AWS services such as AWS Glue or Amazon Athena for further data analysis and querying. S3’s durability and availability ensure that the data is securely stored and can be retrieved at any time for future use.

- **Apache Airflow**: Airflow orchestrates the entire data pipeline, from fetching the data via API calls to processing and storing it in S3. The flexibility of Airflow allows for easy scheduling, dependency management, and monitoring, making it an ideal tool for data engineering workflows. With Airflow, you can set up monitoring alerts, view task logs, and scale your workflows as the project grows in complexity.

### Use Cases:

- **Website reputation monitoring**: This pipeline can be used to regularly monitor the reputation of websites to ensure they remain safe for users. This could be particularly useful for security firms, parental control applications, or businesses that want to ensure they are not linking to harmful sites.
  
- **Domain trustworthiness analysis**: Companies can use the reputation data from the WOT API to evaluate potential partners, suppliers, or affiliates based on the trustworthiness of their domains.
