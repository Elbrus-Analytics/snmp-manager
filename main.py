__author__ = "Hiermann Alexander, Schmidt Tobias"
__version__ = 0.1

# pip install psycopg2
import os
import psycopg2
import ipaddress
from dotenv import load_dotenv

# loads venv variables
load_dotenv()

# establishes a connection using venv variables
connection = psycopg2.connect(
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT")
)


def request_snmp():
    """
    Method used to:
        1) pull snmp-queries from db
        2) build valid 'snmpwalk' commands
        3) execute these commands
        4) pushing response from command back to db

    :return: nothing
    """
    cur = connection.cursor()
    try:
        cur.execute("SELECT * FROM snmp_query")
        for job in cur.fetchall():
            snmp_query = build_snmp_query(job)
            if snmp_query:
                response: str = execute_snmp_query(snmp_query[0])
                if response:
                    push_snmp_to_db(response, job)
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error-0: An error occurred while selecting values from the database:\n${error}")
    finally:
        if cur is not None:
            cur.close()
        if connection is not None:
            connection.close()


def build_snmp_query(row: tuple):
    """
    builds out of the current row (from the select statement), depending on the version, a snmpwalk command

    :param row: tuple, the current row from the select statement
    :return: str, a valid 'snmpwalk' command
    """
    version = row[8]
    if version == 2:
        oid = row[1]
        ip = ipaddress.ip_address(row[2])
        username = row[3]
        if oid and ip and username:
            return "snmpwalk -v2c -c", username, ip, oid
        else:
            print("Error-100: Missing values for SNMPv2 request for Object with id=", row[0], sep='')
    if version == 3:
        oid = row[1]
        ip = ipaddress.ip_address(row[2])
        username = row[3]
        encry_meth = row[4]
        encry_pass = row[5]
        auth_meth = row[6]
        auth_pass = row[7]
        if oid and ip and username and encry_meth and encry_pass and auth_meth and auth_pass:
            return ("snmpwalk -v3 -l authPriv -a", auth_meth, " -A", auth_pass,
                    "-x", encry_meth, "-X", encry_pass, "-u", username, ip, oid)
        else:
            print("Error-101: Missing values for SNMPv3 request for Object with id=", row[0], sep='')


def execute_snmp_query(query: str):
    """
    WIP -> respons muss noch gecheckt werden (ob bekommen/ ob brauchbar)
    :param query: str, command that should be executed
    :return: str, the response from the command
    """
    try:
        # return subprocess.Popen(query, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0])
        return "response101"
        pass
    except Exception as error:
        print(f"Error-102: An error occurred while executing the query:\n${error}")


def push_snmp_to_db(response: str, row: tuple):
    """
    inserts into db table 'snmp_response' --> (oid, reply, usage)
    :param response: str, response from def execute_snmp_query
    :param row: tuple, the current row from the select statement
    :return: nothing
    """
    sql = "Insert into snmp_response(oid, reply, usage) VALUES ('" + str(row[1]) + "', '" + str(
        response) + "', '" + str(row[10]) + "')"
    cur = connection.cursor()
    cur.execute(sql)


if __name__ == "__main__":
    # request_snmp()
    pass
