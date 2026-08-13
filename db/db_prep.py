import os

from dotenv import load_dotenv

os.environ["RUN_TIMEZONE_CHECK"] = "0"

load_dotenv()

from db.db import init_db


if __name__ == "__main__":
    print("Initializing database...")
    init_db()