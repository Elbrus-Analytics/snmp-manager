__author__ = "Hiermann Alexander, Schmidt Tobias"
__version__ = 0.1

# pip install psycopg2

import os
import psycopg2
from dotenv import load_dotenv
import subprocess

load_dotenv()

connection = psycopg2.connect(
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT")
)


def request_snmp():
    cur = connection.cursor()
    try:
        cur.execute('SELECT * FROM snmp_query')
        for job in cur.fetchall():
            snmp_query = build_snmp_query(job)
            if snmp_query:
                response: str = execute_snmp_query(snmp_query[0])
                if response:
                    push_snmp_to_db(response, job)
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if cur is not None:
            cur.close()
        if connection is not None:
            connection.close()


def build_snmp_query(row: list):
    version = row[8]
    if version == 2:
        oid = row[1]
        ip = row[2]
        username = row[3]
        if oid and ip and username:
            return "snmpwalk -v2c -c", username, ip, oid
        else:
            print("missing values for version 2 for Object with id=", row[0], sep='')
    if version == 3:
        oid = row[1]
        ip = row[2]
        username = row[3]
        encry_meth = row[4]
        encry_pass = row[5]
        auth_meth = row[6]
        auth_pass = row[7]
        if oid and ip and username and encry_meth and encry_pass and auth_meth and auth_pass:
            return ("snmpwalk -v3 -l authPriv -a", auth_meth, " -A", auth_pass,
                    "-x", encry_meth, "-X", encry_pass, "-u", username, ip, oid)
        else:
            print("missing values for version 3 for Object with id=", row[0], sep='')


def execute_snmp_query(query: str):
    try:
        # return subprocess.Popen(query, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0])
        return "response101"
        pass
    except Exception as error:
        print(f"Error-102: An error occurred while executing the query:\n${error}")


def push_snmp_to_db(response: str, row: tuple):
    sql = "Insert into snmp_response(oid, reply, usage) VALUES ('" + str(row[1]) + "', '" + str(response) + "', '" + str(row[10]) + "')"
    cur = connection.cursor()
    cur.execute(sql)


if __name__ == "__main__":
    #request_snmp()
