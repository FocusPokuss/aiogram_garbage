from os import environ, path
from dotenv import load_dotenv

load_dotenv(path.join(path.abspath(path.dirname(__file__)), '.env'))

DATABASE_NAME = environ.get('db_name')
DATABASE_HOST = environ.get('db_host')
DATABASE_USERNAME = environ.get('db_username')
DATABASE_PASSWORD = environ.get('db_password')
DATABASE_PORT = environ.get('db_port')
API_TOKEN = environ.get('api_token')
ADMIN_ID = int(environ.get('admin_id'))
