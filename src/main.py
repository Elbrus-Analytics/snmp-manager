__author__ = "Hiermann Alexander, Schmidt Tobias, Markus Tomsik"
__version__ = 1.2

from os import getenv
from datetime import datetime
import logging
import subprocess
import psycopg2
import ipaddress
from dotenv import load_dotenv

SNMP_Query = tuple[int, str, int, str, str | None, str | None, str | None, str | None, int, datetime, str]
"""
SNMP Query returned by the datebase table `snmp_query`

0.  id
1.  oid
2.  ip
3.  username
4.  encryption_method
5.  encryption_passwd
6.  auth_method
7.  auth_passwd
8.  version
9.  time
10. usage
"""

class UnconfiguredEnvironment(Exception):
  """class for unconfigured env vars"""
  pass

def load_enviroment_variables() -> dict[str, str]:
  """
    Custom loader for enviroment variables

    :raises UnconfiguredEnvironment: if a need enviroment variable is missing
  """
  enviroment_variables_list = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "POSTGRES_HOST", "POSTGRES_PORT"]
  envs = dict()

  for var in enviroment_variables_list:
    if not (env_value := getenv(var, None)):
      raise UnconfiguredEnvironment(f"{var} is not configured")
    envs[var] = env_value
  
  return envs


def request_snmp() -> None:
    """
    method used to:
        1) pull snmp-queries from db
        2) build valid 'snmpwalk' commands
        3) execute these commands
        4) pushing response from command back to db

    :return: nothing
    """
    cur = connection.cursor()
    logging.info("000, Started SNMP-request")
    try:
        cur.execute("SELECT * FROM snmp_query")
        for job in cur.fetchall():
            snmp_query = build_snmp_query(job)
            if snmp_query:
                response = execute_snmp_query(snmp_query)
                if response:
                    push_snmp_to_db(job[0], response)
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"100, An error occurred while selecting values from the database:\n{error}")
    finally:
        if cur is not None:
            cur.close()
        if connection is not None:
            connection.close()
        logging.info("001, Finished SNMP-request")


def build_snmp_query(row: SNMP_Query) -> str:
    """
    builds out of the current row (from the select statement), depending on the version, a snmpwalk command

    :param row: SNMP_Query, the current row from the select statement
    :return: str, a valid 'snmpwalk' command
    """
    version = row[8]
    if version == 2:
        oid = row[1]
        ip = ipaddress.ip_address(row[2])
        username = row[3]
        if oid and ip and username:
            return f"snmpwalk -v2c -c {username} {ip} {oid}"
        else:
            logging.error(f"111, Missing values for SNMPv2 request for Object with id={row[0]}")
    if version == 3:
        oid = row[1]
        ip = ipaddress.ip_address(row[2])
        username = row[3]
        encry_meth = row[4]
        encry_pass = row[5]
        auth_meth = row[6]
        auth_pass = row[7]
        if oid and ip and username and encry_meth and encry_pass and auth_meth and auth_pass:
            return f"snmpwalk -v3 -l authPriv -a {auth_meth} -A {auth_pass} -x {encry_meth} -X {encry_pass} -u {username} {ip} {oid}"
        else:
            logging.error(f"112, Missing values for SNMPv3 request for Object with id={row[0]}")


def execute_snmp_query(query: str) -> str:
    """
    Executes snmpwalk shell command

    :param query: str, command that should be executed
    :return: str, the response from the command
    """
    return subprocess.Popen(
        query, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ).communicate()[0].decode("utf-8").split("=")[1].strip()


def push_snmp_to_db(id: int, response: str) -> None:
    """
    inserts into db table 'snmp_response' --> (oid, reply, usage)

    :param response: str, response from def execute_snmp_query
    :param row: tuple, the current row from the select statement
    :return: nothing
    """
    sql = "insert into snmp_response(id, reply) VALUES (%s, %s)"
    cur = connection.cursor()
    cur.execute(sql, (id, response))
    cur.close()


if __name__ == "__main__":
    # load .env file
    load_dotenv()

    try:
        envs = load_enviroment_variables()
    except UnconfiguredEnvironment as err:
        exit(err)

    # setting preferred config for logger
    logging.basicConfig(filename='log/snmp_request.log', filemode='a', format='%(asctime)s, %(levelname)s-%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

    #establishing the connection
    connection = psycopg2.connect(
        database=envs["POSTGRES_DB"],
        user=envs["POSTGRES_USER"],
        password=envs["POSTGRES_PASSWORD"],
        host=envs["POSTGRES_HOST"],
        port=envs["POSTGRES_PORT"]
    )

    request_snmp()
