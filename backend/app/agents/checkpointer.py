import os
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_checkpointer():
    """
    Returns a PostgresSaver checkpointer connected to our database.
    Must call .setup() once to create the necessary tables.
    """
    return PostgresSaver.from_conn_string(DATABASE_URL)
