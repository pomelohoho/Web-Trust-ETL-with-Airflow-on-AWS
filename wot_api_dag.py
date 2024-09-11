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
        ti = kwargs['ti']
        data = ti.xcom_pull(task_ids='fetch_wot_data')

        # Transform the JSON response into a DataFrame
        records_data = []
        for domain, details in data.items():
            record = {
                'Domain': domain,
                'Reputation': details.get('reputation', None),
                'Trustworthiness': details.get('trustworthiness', None),
                'Category': details.get('categories', ["N/A"])[0] if details.get('categories') else None,
                'Safety Confidence': details.get('safety_confidence', None)
            }
            records_data.append(record)

        # Create DataFrame
        df_wot = pd.DataFrame(records_data)
        
        # Save to a CSV file
        csv_path = "/tmp/wot_data.csv"
        df_wot.to_csv(csv_path, index=False)

        # Upload the file to AWS S3
        s3 = boto3.client('s3')
        s3_bucket = 'pom-s3-bucket'  
        s3.upload_file(csv_path, s3_bucket, 'wot_data.csv')

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
