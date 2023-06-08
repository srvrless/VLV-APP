from .database import Database
from tools import parse_html, json_load


class DatabaseUpdater:
    """ Класс для обновления и заполнения базы данных """
    def __init__(self, database: Database) -> None:
        self.database = database

    async def update_all_from_json(self) -> None:
        """ Метод, который будет полностью заполнять базу данными из сохраненных json файлов"""
        pass


    # ==== clients ====

    async def load_clients_from_json(self) -> list:
        """ Считать группы клиентов из json файла """
        return await json_load("clients.json")

    async def update_clients(self, clients: list) -> None:
        """ Функция для заполнения всех групп клиентов """
        await self.database.update_clients(clients)
    
    # ==== client addresses ====
    
    async def update_client_addresses(self, clients: list) -> None:
        """ Функция для заполнения всех групп клиентов """
        await self.database.update_client_addresses(clients)

    # ==== client_groups ====
    async def load_client_groups_from_json(self) -> list:
        """ Считать группы клиентов из json файла """
        return await json_load("client_groups.json")

    async def update_client_groups(self, client_groups: list) -> None:
        """ Функция для заполнения всех групп клиентов """
        await self.database.update_client_groups(client_groups)

    # ==== products ====
    async def load_products_from_json(self) -> list:
        """ Считать товары из json файла """
        return await json_load("products.json")

    async def update_products(self, products: list) -> None:
        """ Функция для заполнения всех товаров """
        await self.database.update_products(products)

    async def update_search_products(self) -> None:
        """ Сформировать таблицу поиска товаров """
        await self.database.update_search_products()


    # ==== properties ====
    async def load_properties_from_json(self) -> list:
        """ Считать свойства товаров из json файла """
        return await json_load("properties.json")

    async def update_properties(self, properties: list) -> None:
        """ Функция для заполнения всех свойств товаров """
        await self.database.update_properties(properties)


    # ==== option_values ====
    async def load_option_values_from_json(self) -> None:
        """ Метод для загрузки категорий из json файла"""
        return await json_load("option_values.json")

    async def update_option_values(self, option_values) -> None:
        """ Метод для заполнения таблицы с категориями """
        await self.database.update_option_values(option_values)
    

    # ==== option_names ====
    async def load_option_names_from_json(self) -> None:
        """ Метод для загрузки категорий из json файла"""
        return await json_load("option_names.json")

    async def update_option_names(self, option_names) -> None:
        """ Метод для заполнения таблицы с категориями """
        await self.database.update_option_names(option_names)


    # ==== categories ====
    async def load_categories_from_json(self) -> None:
        """ Метод для загрузки категорий из json файла"""
        return await json_load("categories.json")

    async def update_categories(self, categories) -> None:
        """ Метод для заполнения таблицы с категориями """
        await self.database.update_categories(categories)


    # ==== collections ====
    async def load_collections_from_json(self) -> None:
        """ Метод для загрузки коллекций из json файла"""
        return await json_load("collections.json")

    async def update_collections(self, collections) -> None:
        """ Метод для заполнения таблицы с коллекциями """
        await self.database.update_collections(collections)

