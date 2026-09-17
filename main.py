from dotenv import load_dotenv

from api.app import app

load_dotenv()

__all__ = ["app"]
