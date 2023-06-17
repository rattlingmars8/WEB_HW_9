"""
Підключення до MongoDB за допомогою mongoengine.
Зчитуємо параметри підключення до MongoDB з конфігураційного файлу config.ini.
Використовуючи отримані параметри робимо підключення до MongoDB.
"""

from mongoengine import connect
import configparser
from pathlib import Path

config_ini = Path(__file__).parent.joinpath("config.ini")

config = configparser.ConfigParser()
config.read(config_ini)

mongo_user = config.get('DB', 'USER')
mongo_pass = config.get('DB', 'PASS')
mongo_domain = config.get('DB', 'DOMAIN')
mongo_db_name = config.get('DB', 'DATA_BASE')

connect(
    host=f"mongodb+srv://{mongo_user}:{mongo_pass}@{mongo_domain}/{mongo_db_name}?retryWrites=true&w=majority", ssl=True
)

