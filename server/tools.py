
import os
import http_code
import json 
import string
import asyncio
import dateutil.parser
import platform

from bs4 import BeautifulSoup
from functools import wraps
from quart import jsonify, request
from service import TokenProcess
from config import JSON_PATH
from typing import Any
from aiohttp import ClientSession
from datetime import datetime 
from slugify import slugify


if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class Translitor:
    """ Класс для преобразования русских названий свойств в английские для передачи в json формате """
    def __init__(self, database) -> None:
        self.database = database
        
        self.ru_to_eng_dict = dict()
        self.eng_to_ru_dict = dict()

    def title_to_eng(self, title: str) -> str:
        """ Убирает из названия пунктуацию, заменяет пробелы на нижние подчеркивания, приводит к нижнему регистру и делает транслит """
        title = title.translate(str.maketrans("", "", string.punctuation))
        title = title.replace(" ", "_").lower()
        title = slugify(title, separator="_", lowercase=True)
        return title

    def init(self) -> None:
        """ Инициация, получение из базы названий свойств и опций """
        properties = asyncio.run(self.database.get_properties())
        options = asyncio.run(self.database.get_option_names())
        titles = [c["title"] for c in properties + options]
        eng_titles = [self.title_to_eng(t) for t in titles]
        self.ru_to_eng_dict = dict(zip(titles, eng_titles))
        self.eng_to_ru_dict = dict(zip(eng_titles, titles))

    def ru_to_eng(self, title: str) -> str:
        """ Русское название в английское """
        return self.ru_to_eng_dict[title]

    def eng_to_ru(self, title: str) -> str:
        """ Английское название в русское """
        return self.eng_to_ru_dict[title]

    def is_in_eng_titles(self, title: str) -> bool:
        """ True / False находится ли название в списке """
        return title in self.eng_to_ru_dict
    
    def is_in_ru_titles(self, title: str) -> bool:
        """ True / False находится ли название в списке """
        return title in self.ru_to_eng_dict
    
    def option_from_eng_to_ru(self, option: str) -> str:
        """ Приведение опции из query запроса к формату бд """
        values = option.split("-")
        left = self.eng_to_ru(values[0])
        return left + " " + "-".join(values[1:])



async def async_request_json(url: str, params: dict = {}) -> Any:
    """ Асинхронные http запросы """
    async with ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            return await response.json()

def parse_html(html_document: str) -> str:
    """ Метод для парсинга html текста. Убирает из текста теги и лишние символы """
    try:
        soup = BeautifulSoup(html_document, 'html.parser')
        text = soup.get_text()
        text = text.replace('Описание', '').replace('  ', ' ')
        return text
    except TypeError: return ''

def parse_timestamp(time_string: str) -> datetime:
    """ Функция для парсинга времени в ISO формате """
    return dateutil.parser.isoparse(time_string)

def parse_quantity_at_warehouses(variant: dict) -> list[int]:
    """ Парсинг json объекта variant для получения количества товара на складах/в магазинах """
    quantities = []
    i = 0
    while f"quantity_at_warehouse{i}" in variant:
        quantities.append(int(float(variant[f"quantity_at_warehouse{i}"])))
        i += 1
    return quantities

def parse_null_float(number: str | None):
    """ Преобразует число из типа str по float, либо возвращает None, если передан None"""
    return float(number) if number is not None else None

def validate_args(info, required: tuple[str] | str, possible: tuple[str] | str) -> tuple[bool, str]:
    """ Валидация аргументов (используется декораторами query_args и json_args) """
    if isinstance(required, str): required = (required, )
    if isinstance(possible, str): possible = (possible, )

    if not all(k in info for k in required):
        not_sent = ", ".join([n for n in required if n not in info])
        return False, f"не хватает полей: {not_sent}"

    all_args = required + possible
    unnecessary = [k for k in info if k not in all_args]
    if len(unnecessary) > 0:
        unnecessary = ", ".join(unnecessary)
        return False, f"лишние поля: {unnecessary}"

    return True, "Все окей"


def query_args(required: tuple[str] | str = tuple(), possible: tuple[str] | str = tuple()):
    """ Декоратор, который проверяет все ли нужные поля в query string присутствуют и нет ли лишних """
    def decorator(func):

        @wraps(func)
        async def inner_decorator(*args, **kwargs):
            info = request.args.to_dict()
            
            is_ok, error_text = validate_args(info, required, possible)
            if is_ok:            
                return await func(*args, **kwargs)
            else:
                return jsonify({"message": "В query string " + error_text}), http_code.bad_request
        return inner_decorator 
    
    return decorator    


def json_args(required: tuple[str] | str = tuple(), possible: tuple[str] | str = tuple()):
    """ Декоратор, который проверяет все ли нужные поля в отправленном json присутствуют и нет ли лишних """
    def decorator(func):
        @wraps(func)
        async def inner_decorator(*args, **kwargs):
            info = await request.get_json()

            is_ok, error_text = validate_args(info, required, possible)
            if is_ok:            
                return await func(*args, **kwargs)
            else:
                return jsonify({"message": "В json " + error_text}), http_code.bad_request
        return inner_decorator 
    
    return decorator    


token_process = TokenProcess()
# TODO добавить проверку срока годности токена
def token_required(f):
    """ Декоратор, автоматически проверяющий токен в запросе """
    @wraps(f)
    async def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            try:
                token = request.headers["Authorization"].split(" ")[1]
            except:
                return jsonify({"message": "Не передан токен"}), http_code.bad_request
        else:
            return jsonify({"message": "Не передан заголовок Authorization"}), http_code.bad_request
        if not token:
            return jsonify({"message": "Не передан токен"}), http_code.bad_request
        try:
            user_email = await token_process.get_email_from_token(token)
        except Exception as e:
            return jsonify({"message": "Ошибка при обработке токена", "error": str(e)}), http_code.internal_server_error
        return await f(user_email, *args, **kwargs)

    return decorated


async def json_save(file_name: str, json_object: Any) -> None:
    """ Метод для сохранения json объекта в папку со статикой """
    os.makedirs(JSON_PATH, exist_ok=True)
    with open(JSON_PATH + "/" + file_name, "w") as f:
        json.dump(json_object, f)


async def json_load(file_name: str) -> Any:
    """ Метод для загрузки json объекта из папки со статикой """
    os.makedirs(JSON_PATH, exist_ok=True)
    with open(JSON_PATH + "/" + file_name) as f:
        return json.load(f)
    
# async def json_save(file_name: str, json_object: Any) -> None:
#     """ Метод для сохранения json объекта в папку со статикой """
#     os.makedirs(JSON_PATH, exist_ok=True)
    
#     with open(JSON_PATH + "/" + file_name, "w", encoding="utf-8") as f:
#         json.dump(json_object, f, ensure_ascii=False)



