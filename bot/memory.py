from dotenv import dotenv_values # type: ignore
from langgraph.checkpoint.postgres import PostgresSaver # type: ignore

config = dotenv_values(".env")

DB_URI = config.get("DB")
with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()