import os
import mysql.connector
from dotenv import load_dotenv
load_dotenv()

class Database:
    def __init__(self):
        self.conn=mysql.connector.connect(
            
            #host="localhost",
            #user="root",
            #password="",
            #database="balota"
            
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            port=os.getenv("PORT"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DB")
        )

            