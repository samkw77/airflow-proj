from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.exceptions import AirflowFailException
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import psycopg2
import pandas as pd
import sys


# Add project path for Airflow to import existing functions
sys.path.append("/opt/stocks-proj")
from ingestion.fetch_stocks import fetch_multiple_stocks, insert_to_postgres


# -------------------------
# Config
# -------------------------
default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


# -------------------------
# Task functions
# -------------------------
def fetch_and_store():
    symbols = ["CRWD", "PLTR"]
    df = fetch_multiple_stocks(symbols)
    insert_to_postgres(df)


def validate_raw_data():
    conn = psycopg2.connect(
        host="postgres",
        dbname="stock_pipeline",
        user="skwong",
        password="postgres"
    )
    df = pd.read_sql("SELECT * FROM raw_stock_prices", conn)

    # # Use hook to avoid hardcoding creds;
    # # pdate postgres_default in Airflow UI first

    # hook = PostgresHook(postgres_conn_id="postgres_default")
    # df = hook.get_pandas_df("SELECT * FROM raw_stock_prices")
    
    # Check for nulls and duplicates
    if df.empty:
        raise AirflowFailException("No data in raw_stock_prices!")

    if df['date'].isnull().any() or df['symbol'].isnull().any():
        raise AirflowFailException("Nulls found in critical columns!")

    if df.duplicated(subset=['date', 'symbol']).any():
        raise AirflowFailException("Duplicate (date, symbol) found!")

    # Check for invalid prices
    if (df[['open','high','low','close']] < 0).any().any():
        raise AirflowFailException("Negative price found!")
    
    conn.close()
    print("Data validation passed.")


# -------------------------
# DAG
# -------------------------
with DAG(
    dag_id="stock_pipeline",
    start_date=datetime(2026, 3, 24),
    schedule_interval="@daily",
    catchup=False,
    default_args=default_args,
) as dag:

    fetch_task = PythonOperator(
        task_id="fetch_and_store",
        python_callable=fetch_and_store
    )

    validate_task = PythonOperator(
        task_id="validate_data",
        python_callable=validate_raw_data
)

    dbt_task = BashOperator(
        task_id="run_dbt",
        bash_command="cd /opt/stocks-proj/dbt && dbt run"
    )

    fetch_task >> validate_task >> dbt_task
