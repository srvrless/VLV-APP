
import os
from dotenv import load_dotenv

load_dotenv()


INSALES_URL = 'https://26c60c2c500a6c6f1af7aa91d11c197c:a5f07ba6e0c4738819d1ba910731db57@myshop-bte337.myinsales.ru/admin'
ADDR_FROM = 'kshleigel@yandex.ru'
EMAIL_PASSWORD = 'OmegaSolarFive-1848'

STATIC_PATH = "server/static"
JSON_PATH = "server/static"

DATABASE_HOST = os.environ.get('DB_HOST')
DATABASE_PORT = os.environ.get('DB_PORT')
DATABASE_NAME = os.environ.get('DB_NAME')
DATABASE_USER = os.environ.get('DB_USER')
DATABASE_PASSWORD = os.environ.get('DB_PASS')