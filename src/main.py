__author__ = "Alexander Hiermann"
__version__ = "2.1"
__since__ = "2022/07/17"

import os
from datetime import datetime
from os import getenv
from dotenv import load_dotenv
import logging
import psycopg2
import subprocess
from typing import Generator
import ipaddress
from datetime import date

"""
This variable is used to store the result of the snmp request

Indexes with it's snmp related meanings

0.  id -> primary key for db
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
SNMP_Query = tuple[int, str, int, str, str | None, str | None, str | None, str | None, int, datetime, str]


class MissingEnvironmentConfigurationException(Exception):
    """
    This class is used to throw a new exception if the given environment is not fully initialized
    """
    pass


def load_environment_variables() -> dict[str, str]:
    """
    Used to load all needed environment_variables.

    Please consider updating this method if any new variables are added to the environment!
    :return: envs, dict[str, str] with key and value of each variable
    """
    env_vars_list = ["SHAREDCONFIG", "LOGFILEDIR"]
    envs = dict()

    for var in env_vars_list:
        if not (env_value := getenv(var)):
            raise MissingEnvironmentConfigurationException(f"The given environment is not fully initialized: {var} is "
                                                           f"not configured")
        envs[var] = env_value

    return envs


def request_snmp_queries() -> Generator[SNMP_Query, None, None]:
    """
    Used to receive all needed snmp queries from the database. These queries are later on sent as snmp requests.
    :return yields each query from the db
    """
    with connection.cursor("snmp_query_cursor") as curs:
        curs.execute("SELECT * FROM snmp_query")
        while (query := curs.fetchone()) is not None:
            yield query


def request_snmp() -> None:
    """
    Used to:
        1) pull snmp-queries from db
        2) build valid 'snmpwalk' commands
        3) execute these commands
        4) pushing response from command back to db
    """
    logging.info("000, Started SNMP-request")
    try:
        for job in request_snmp_queries():
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
    Used to build a snmpwalk command out of the current row (from the select statement)

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
    Used to execute the snmpwalk bash command

    :param query: str, command that should be executed
    :return: str, the response from the command
    """
    return subprocess.Popen(
        query, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    ).communicate()[0].decode("utf-8").split("=")[1].strip()


def push_snmp_to_db(pk_id: int, reply: str) -> None:
    """
    Used to insert the gotten data into db table 'snmp_response' --> (oid, reply)

    :param reply: str, response to snmp request
    :param pk_id: int, id of snmp request in db
    """
    sql = "INSERT INTO snmp_response(id, reply) VALUES (%s, %s)"
    cur = connection.cursor()
    cur.execute(sql, (pk_id, reply))
    cur.close()


if __name__ == '__main__':
    load_dotenv()
    env_vars = load_environment_variables()
    
    # logging related:
    log_file_dir = env_vars["LOGFILEDIR"]
    if not os.path.exists(log_file_dir):
        os.makedirs(log_file_dir)

    logging.basicConfig(filename=f'{log_file_dir}/snmp-manager-{date.today()}.log', filemode='a',
                        format='%(asctime)s {%(levelname)s} %(message)s',
                        datefmt='[%Y-%m-%d %H:%M:%S%z]', level=logging.INFO)

    # database related:
    load_dotenv(env_vars["SHAREDCONFIG"])

    logging.info('an info message')
    logging.debug('a debug messag is not shown')

    connection = psycopg2.connect(
        database = getenv('DB_NAME'),
        user = getenv('DB_USER'),
        password = getenv('DB_PASSWORD'),
        host = getenv('DB_HOST'),
        port = getenv('DB_PORT')
    )
    #request_snmp()
