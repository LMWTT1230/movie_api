import csv

import sqlalchemy

from src.datatypes import Character, Movie, Conversation, Line
import os
import dotenv

# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"


# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url())
metadata_obj = sqlalchemy.MetaData()
movie = sqlalchemy.Table("movie", metadata_obj, autoload_with = engine)
character = sqlalchemy.Table("character", metadata_obj, autoload_with = engine)
line = sqlalchemy.Table("line", metadata_obj, autoload_with = engine)
conversation = sqlalchemy.Table("conversation", metadata_obj, autoload_with = engine)

