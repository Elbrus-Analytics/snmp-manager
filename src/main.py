from typing import Generator
from os import getenv
from datetime import datetime
from sys import exit
import logging
import subprocess
import psycopg2
import ipaddress
from dotenv import load_dotenv

SNMP_Query = tuple[int, str, int, str, str | None, str | None, str | None, str | None, int, datetime, str]
"""
snmp query returned by the database table 'snmp_query'

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


class MissingEnvironmentConfigurationException(Exception):
    """
    class for missing configured environment variables
    """
    pass


def load_environment_variables() -> dict[str, str]:
    """
      custom loader for environment variables

      :raises UnconfiguredEnvironment: if a needed environment variable is missing
    """
    environment_variables_list = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB", "POSTGRES_HOST", "POSTGRES_PORT"]
    envs = dict()

    for var in environment_variables_list:
        if not (env_value := getenv(var, None)):
            raise MissingEnvironmentConfigurationException(f"{var} is not configured")
        envs[var] = env_value

    return envs


def get_all_snmp_queries() -> Generator[SNMP_Query, None, None]:
    """get all snmp queries from the database"""
    with connection.cursor("snmp_query_cursor") as curs:
        curs.execute("SELECT * FROM snmp_query")
        while (query := curs.fetchone()) is not None:
            yield query


def request_snmp() -> None:
    """
    method used to:
        1) pull snmp-queries from db
        2) build valid 'snmpwalk' commands
        3) execute these commands
        4) pushing response from command back to db
    """
    logging.info("000, Started SNMP-request")
    try:
        for job in get_all_snmp_queries():
            if snmp_query := build_snmp_query(job):
                if response := execute_snmp_query(snmp_query):
                    push_snmp_to_db(job[0], response)
        connection.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(f"100, An error occurred while selecting values from the database:\n{error}")
    finally:
        if connection is not None:
            connection.close()
        logging.info("001, Finished SNMP-request")


def build_snmp_query(row: SNMP_Query) -> str:
    """
    builds a snmpwalk command out of the current row (from the select statement)

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
    Executes snmpwalk bash command

    :param query: str, command that should be executed
    :return: str, the response from the command
    """
    return subprocess.Popen(
        query, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ).communicate()[0].decode("utf-8").split("=")[1].strip()


def push_snmp_to_db(id: int, response: str) -> None:
    """
    inserts into db table 'snmp_response' --> (oid, reply)

    :param response: str, response to snmp request
    :param row: tuple, the current row from the select statement
    """
    sql = "insert into snmp_response(id, reply) VALUES (%s, %s)"
    cur = connection.cursor()
    cur.execute(sql, (id, response))
    cur.close()


if __name__ == "__main__":
    # load .env file
    load_dotenv()

    try:
        envs = load_environment_variables()
    except MissingEnvironmentConfigurationException as err:
        exit(err)

    # setting preferred config for logger
    logging.basicConfig(filename='log/snmp_request.log', filemode='a', format='%(asctime)s, %(levelname)s-%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)

    # establishing the connection
    connection = psycopg2.connect(
        database=envs["POSTGRES_DB"],
        user=envs["POSTGRES_USER"],
        password=envs["POSTGRES_PASSWORD"],
        host=envs["POSTGRES_HOST"],
        port=envs["POSTGRES_PORT"]
    )

    request_snmp()
