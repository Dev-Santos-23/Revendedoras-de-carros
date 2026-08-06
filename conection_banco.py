import psycopg2
import os
from dotenv import load_dotenv
from fastapi import Depends

load_dotenv()
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_db():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password=DB_PASSWORD,
        dbname="carros"
    )
    try:
        yield conn
    finally:
        conn.close()


        



