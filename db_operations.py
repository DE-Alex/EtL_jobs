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

def connect_to_db():
    try:
        conn = psycopg.connect(
            "dbname=" + dbname
            + " user=" + user
            + " password=" + password
            + " host=" + host,
            port = port)
    except psycopg.OperationalError as e:
        print('psycopg.OperationalError:', e)
        return exit(1)
    return conn
        
def id_from_db():
    conn = connect_to_db()
    with conn.cursor() as curs:
        result = curs.execute(f"SELECT id FROM {table_name};").fetchall()
    conn.close()
    jobs_id = [item[0] for item in result]
    return jobs_id
    
def col_names_from_db():
    conn = connect_to_db()
    with conn.cursor() as curs:
        curs.execute(f"SELECT * FROM {table_name} LIMIT 0;")
        columns = [desc[0] for desc in curs.description]
    conn.close()
    return columns
   
def drop_to_db(jobs, jobs_id):
    jobs_to_insert = [job for job in jobs if int(job['id']) not in jobs_id]
    jobs_to_update = [job for job in jobs if int(job['id']) in jobs_id]
    ins_count, upd_count = 0, 0

    #Insert jobs
    ins_id, upd_id = [], []
    if len(jobs_to_insert) > 0:
        try:
            conn = connect_to_db()
            with conn.cursor() as curs:
                for job in jobs_to_insert:
                    columns = list(job.keys())
                    placeholders = (', ').join(['%s']*len(columns))
                    cols_str = (', ').join([f'"{name}"' for name in columns]) #"quote" columns to escape lowercase by PostgreSQL
                    values = [job[key] for key in columns] #form set of values in order by columns
                    
                    query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})RETURNING id;"
                    curs.execute(query, values)
                    ins_id.append(curs.fetchone()[0])
                conn.commit()
            conn.close()
            ins_count = ins_count + len(ins_id)
        except psycopg.Error as e:
            print(e)
            conn.rollback()
            conn.close()

    #Update jobs
    if len(jobs_to_update) > 0:
        try:
            conn = connect_to_db()
            with conn.cursor() as curs:
                for job in jobs_to_update:
                    columns = list(job.keys())
                    placeholders = (', ').join([f'"{key}"=%s' for key in columns]) #"quote" columns to escape lowercase by PostgreSQL
                    values = [job[key] for key in columns] #form set of values in order by columns

                    query = f"UPDATE {table_name} SET {placeholders} WHERE id = {job['id']} RETURNING id;"
                    curs.execute(query, values)
                    upd_id.append(curs.fetchone()[0])
                conn.commit()
            conn.close()
            upd_count = upd_count + len(upd_id)
        except psycopg.Error as e:
            print(e)
            conn.rollback()
            conn.close()
    return ins_count, upd_count, ins_id
    
    
if __name__ == '__main__':
    jobs_id = id_from_db()
    print('len:', len(jobs_id))
    for id in jobs_id:
        print(id)
        input()
