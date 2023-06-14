import asyncio
from concurrent.futures import ProcessPoolExecutor
from config import INSALES_URL
from tools import async_request_json

import requests
from aiohttp import ClientSession

# Количество товаров при обращении к api за раз
MAX_PRODUCT_PER_PAGE = 250
MAX_CLIENT_PER_PAGE = 10

USER_AGENT_VAL = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"



URL_LOGIN = "https://vivalavika.com/client_account/login"
URL_SESSION = "https://vivalavika.com/client_account/session"
DOMAIN = ".vivalavika.com"

SUCCESS_URL_LOGIN = "https://vivalavika.com/client_account/orders"

URL_REGISTER = "https://vivalavika.com/client_account/contacts/new"
URL_CONTACTS = "https://vivalavika.com/client_account/contacts"

# /client_account/contacts

class InsalesApi:
    """ Класс для всех обращений напрямую к InSales """
    def __init__(self) -> None:
        pass

    async def login(self, email: str, password: str) -> bool:
        """ Метод для логина пользователя. Отправляет данные в форму на сайте и проверяет получаемые хедеры """
        async with ClientSession() as session:
            async with session.get(url=URL_LOGIN, headers={"User-Agent": USER_AGENT_VAL}) as response:
                _xsrf = response.cookies.get('_xsrf')

            session.headers.update({'Referer': URL_LOGIN})
            session.headers.update({'User-Agent': USER_AGENT_VAL})

            async with session.post(URL_SESSION, json={'email': email, 'password': password, '_xsrf': _xsrf}) as response:
                return str(response.url) == SUCCESS_URL_LOGIN
            
            
    async def register(self, contact_name: str, surname: str, phone: str, email: str, password: str, password_confirmation: str, birth_date: str = "") -> tuple[bool, str]:
        """ Метод для регистрации пользователя. Отправляет данные в форму на сайте и проверяет получаемые хедеры """
        async with ClientSession() as session:
            async with session.get(url=URL_REGISTER, headers={"User-Agent": USER_AGENT_VAL}) as response:
                _xsrf = response.cookies.get('_xsrf')

            session.headers.update({'Referer': URL_REGISTER})
            session.headers.update({'User-Agent': USER_AGENT_VAL})

            json_data = {
                "client[registered]": "1",
                "client[contact_name]": "Евгений",
                "client[surname]": "Токарев",
                "client[phone]": "8(800)555-35-35",
                "client[email]": "tok736@gmail.com",
                "client[fields_values_attributes][26935354][hack]": "",
                "client[fields_values_attributes][26935354][field_id]": "26935354",
                "client[fields_values_attributes][26935354][value]": "22.05.2000",
                "client[password]": "00_22_00_At",
                "client[password_confirmation]": "00_22_00_At",
                "client[consent_to_personal_data]": [
                    "0",
                    "1"
                ]
            }

            async with session.post(URL_CONTACTS, data=json_data) as response:
                print(response.headers)
                print(response.cookies)
                print(response.url)
            
                with open("hh_success.html", "w",encoding="utf-8") as f:
                    f.write(await response.text())

    async def get_client_groups(self) -> list:
        """Получить список всех групп клиентов"""
        return await async_request_json(INSALES_URL + "/" + "client_groups.json") 
    
    async def get_clients(self) -> list:
        """Получить список всех клиентов"""
        clients = []
        page = 1
        while page <= MAX_CLIENT_PER_PAGE:
            result = await async_request_json(INSALES_URL + "/" + "clients.json",
                                          params={"page": page, "per_page": MAX_CLIENT_PER_PAGE})
            if len(result) == 0: 
                break

            clients.extend(result)
            page += 1

        return clients 

    async def get_properties(self) -> list:
        """Получить список всех значений свойств"""
        return await async_request_json(INSALES_URL + "/" + "properties.json") 

    async def get_option_values(self) -> list:
        """Получить список всех значений опций"""
        return await async_request_json(INSALES_URL + "/" + "option_values.json")    

    async def get_option_names(self) -> list:
        """Получить список всех имен опций"""
        return await async_request_json(INSALES_URL + "/" + "option_names.json")

    async def get_collections(self) -> list:
        """Получить список всех коллекций"""
        return await async_request_json(INSALES_URL + "/" + "collections.json")
    
    async def get_categories(self) -> list:
        """Получить список всех категорий"""
        return await async_request_json(INSALES_URL + "/" + "categories.json")

    async def get_max_products_per_page(self) -> int:
        """Сколько товаров максимум берется за раз"""
        return MAX_PRODUCT_PER_PAGE

    async def get_products_count(self) -> int:
        """Получить количество товаров"""
        result = await async_request_json(INSALES_URL + "/" + "products/count.json")
        return result["count"]

    async def get_products_on_page(self, page: int, per_page: int = MAX_PRODUCT_PER_PAGE) -> list:
        """Получить партию товаров по 250 штук (по умолчанию) на определенной странице"""
        result = await async_request_json(INSALES_URL + "/" + "products.json",
                                          params={"page": page, "per_page": per_page})
        return result
    
    async def get_all_products(self) -> list:
        """Получить все товары"""
        count = await self.get_products_count()
        result = []
        for page in range(1, count // MAX_PRODUCT_PER_PAGE + 2):
            result.extend(await self.get_products_on_page(page))
        return result

    async def get_all_properties(self) -> list:
        """Получить все свойства товаров"""
        return await async_request_json(INSALES_URL + "/" + "properties.json")
        