from datetime import timedelta
from airflow import DAG
from airflow.operators.bash_operator \
      import BashOperator
from airflow.utils.dates import days_ago

dag = DAG(
    'Upwork',
    description='Check and download jobs from www.upwork.com',
    schedule_interval=timedelta(minutes=10),
    start_date = days_ago(1),
    catchup=False,
)


t1 = BashOperator(
    task_id='check_new_jobs',
    depends_on_past=False,
    bash_command='~/upwork_scanner/env/bin/python ~/upwork_scanner/scripts_upwork/upwork1_check.py',
    dag=dag,
)

t2 = BashOperator(
    task_id='download_jobs',
    depends_on_past=False,
    bash_command='~/upwork_scanner/env/bin/python ~/upwork_scanner/scripts_upwork/upwork2_download.py',
    dag=dag,
)

t1 >> t2
