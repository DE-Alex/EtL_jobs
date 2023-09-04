import configparser
import sys
import psycopg
from pathlib import Path

config = configparser.ConfigParser()
config.read(Path(sys.path[0], 'pipeline.conf'))

dbname = config["postgres_config"]["database"]
user = config["postgres_config"]["username"]
password = config["postgres_config"]["password"]
host = config["postgres_config"]["host"]
port = config["postgres_config"]["port"]
table_name = config['upwork']['upwork_table']

def id_from_db():
    conn = psycopg.connect(
        "dbname=" + dbname
        + " user=" + user
        + " password=" + password
        + " host=" + host,
        port = port)
        
    id_query = f"SELECT id FROM {table_name};"
    cursor = conn.cursor()
    cursor.execute(id_query)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    
    jobs_id = [item[0] for item in result]
    return jobs_id
    
if __name__ == '__main__':
    jobs_id = id_from_db()
    print('len:', len(jobs_id))
    for id in jobs_id:
        print(id)
        input()
