__author__ = "Hiermann Alexander, Schmidt Tobias"
__version__ = 0.1
# pip install psycopg2

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

connection = psycopg2.connect(
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT")
)


if __name__ == "__main__":
    sql = """Insert into snmp_query(oid, ip, version, usage)
    VALUES ('iso.3.2.3.5432.12.6', 345668, 1, 'interface usage');
    """
    cur = connection.cursor()
    #cur.execute(sql)
    #connection.commit()
    cur.execute('SELECT * FROM snmp_query')
    response = cur.fetchall()
    print(str(response).split(',')[1])
    cur.close()


def request_snmp():
    build_snmp_query()
    execute_snmp_query()
    push_snmp_to_db()


def build_snmp_query(row:list):
    oid = row[1]
    ip = row[2]
    username = row[3]
    encry_meth = row[4]
    encry_pass = row[5]
    auth_meth = row[6]
    auth_pass = row[7]
    version = row[8]



def execute_snmp_query(query:str):
    pass


def push_snmp_to_db(response:str, row:list):
    pass