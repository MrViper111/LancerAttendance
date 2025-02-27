import os

import motor.motor_asyncio
from dotenv import load_dotenv


class Database:

    load_dotenv()

    URI = os.getenv("DB_URI")
    NAME = os.getenv("DB_NAME")

    @staticmethod
    def establish_connection(uri, database_name):
        mongo_client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        return mongo_client[database_name]
