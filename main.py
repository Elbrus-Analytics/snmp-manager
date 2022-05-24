__author__ = "Hiermann Alexander, Schmidt Tobias"
__version__ = 0.1
# pip install psycopg2

import os
import psycopg2

connection = psycopg2.connect(
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT")
)

