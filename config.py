import os

from dotenv import load_dotenv


load_dotenv()

REMOTE_HOST = os.getenv("REMOTE_HOST")
REMOTE_PATH = os.getenv("REMOTE_PATH")


if not REMOTE_HOST:
    raise RuntimeError(
        "REMOTE_HOST is not configured. "
        "Create a .env file based on .env.example."
    )

if not REMOTE_PATH:
    raise RuntimeError(
        "REMOTE_PATH is not configured. "
        "Create a .env file based on .env.example."
    )


DESTINATION = f"{REMOTE_HOST}:{REMOTE_PATH}"