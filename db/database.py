import config
import asyncpg
from service import TokenProcess
from tools import parse_html, parse_timestamp, parse_quantity_at_warehouses, parse_null_float

token_process = TokenProcess()

# TODO добавить методы для удаления товаров/коллекций
# TODO добавить метод обновления таблицы поиска товаров
# TODO продумать логику перевода гостевых аккаунтов в настоящие

EXCLUDED_CHARACTERS = {" ", ",", "-", ";"}

class Database:
    """ Класс для работы с базой данных """
    def __init__(self):
        self.host = config.DATABASE_HOST
        self.db_name = config.DATABASE_NAME
        self.dbuser = config.DATABASE_USER
        self.password = config.DATABASE_PASSWORD
        self.port = config.DATABASE_PORT
        self.is_connected = False

    

    # ==== login / authorization ====

    async def guest_login(self, email) -> dict:
        """ Функция для гостевого логина """
        client_data = dict()
        
        clients = await self.select_many("SELECT * FROM client WHERE email = $1;", email, close=False)
        client_data["client_id"] = None

        client_data["was_in_database"] = len(clients) > 0

        if client_data["was_in_database"]:
            client = clients[0]
            client_data["is_guest"] = client["is_guest"]
            if client_data["is_guest"]:
                client_data["message"] = "Найден гостевой аккаунт"
                client_data["client_id"] = client["id"]
            else:
                client_data["message"] = "Пользователь с таким email уже зарегистрирован, авторизуйтесь"
        else:
            await self.execute_one("SELECT * FROM add_guest_account($1);", email, start=False, close=False)
            clients = await self.select_many("SELECT * FROM client WHERE email = $1;", email, close=False)
            client_data["is_guest"] = True
            client_data["message"] = "Создан новый гостевой аккаунт"
            client_data["client_id"] = clients[0]["id"]

        if self.is_connected:
            self.close_connection()

        return client_data

    # ==== clients ====

    async def get_client_by_email(self, email) -> None:
        values = await self.execute_one("SELECT * FROM client WHERE email = $1;", email, close=False)
        if len(values) > 0:
            client = values[0]
            
            address_id = client["default_address_id"]
            address = await self.execute_one("SELECT * FROM address WHERE id = $1;", address_id, start=False, close=False)
            client["default_address"] = address[0] if len(address) > 0 else None

            client_group_id = client["client_group_id"]
            client_group = await self.execute_one("SELECT * FROM client_group WHERE id = $1;", client_group_id, start=False)
            client["default_client_group"] = client_group[0] if len(client_group) > 0 else None
            return client
        else:
            self.close_connection()
            return dict()


    async def update_clients(self, clients: list) -> None:
        """ Функция для добавления/удаления новых значений опций """
        columns = ("id", "email", "name", "phone", "registered", "client_group_id", 
                   "surname", "middlename", "bonus_points", "type", "contact_name", "ip_addr", 
                   "birth_date", "default_address_id", "full_name")
        values = [(c["id"], c["email"], c["name"], c["phone"], c["registered"], c["client_group_id"],
                   c["surname"], c["middlename"], c["bonus_points"], c["type"], c["contact_name"], c["ip_addr"],
                   c["fields_values"][0]["value"] if len(c["fields_values"]) > 0 else None, 
                   c["default_address"]["id"] if c["default_address"] is not None else None, 
                   c["full_name"]) for c in clients]
        await self.execute_many("client", columns, values)

    # ==== client addresses ====

    async def update_client_addresses(self, clients: list) -> None:
        """ Функция для добавления/удаления новых значений опций """
        columns = ("id", "phone", "full_locality_name", 
                   "full_delivery_address", "address_for_gis", "location_valid", 
                   "address", "country", "state", 
                   "city", "zip", "kladr_code", 
                   "kladr_zip", "region_zip", "area", 
                   "area_type", "settlement", "settlement_type", 
                   "street", "street_type", "house", 
                   "flat", "is_kladr", "latitude", 
                   "longitude")
        values = [(c["default_address"]["id"], c["default_address"]["phone"], c["default_address"]["full_locality_name"],
                   c["default_address"]["full_delivery_address"], c["default_address"]["address_for_gis"], c["default_address"]["location_valid"],
                   c["default_address"]["address"], c["default_address"]["country"], c["default_address"]["state"],
                   c["default_address"]["city"], c["default_address"]["zip"], c["default_address"]["location"]["kladr_code"],
                   c["default_address"]["location"]["kladr_zip"], c["default_address"]["location"]["region_zip"], c["default_address"]["location"]["area"],
                   c["default_address"]["location"]["area_type"], c["default_address"]["location"]["settlement"], c["default_address"]["location"]["settlement_type"],
                   c["default_address"]["location"]["street"], c["default_address"]["location"]["street_type"], c["default_address"]["location"]["house"],
                   c["default_address"]["location"]["flat"], c["default_address"]["location"]["is_kladr"], c["default_address"]["location"]["latitude"],
                   c["default_address"]["location"]["longitude"]) for c in clients if c["default_address"] is not None]
        await self.execute_many("address", columns, values)

    # ==== client_groups ====

    async def update_client_groups(self, client_groups: list) -> None:
        """ Функция для добавления/удаления новых значений опций """
        columns = ("id", "title", "discount", "discount_description", "is_default")
        values = [(c["id"], c["title"], c["discount"], c["discount_description"], c["is_default"]) for c in client_groups]
        await self.execute_many("client_group", columns, values)


    # ==== products ====

    async def update_search_products(self) -> None:
        await self.select_many("SELECT * FROM update_search_products();")

    async def get_product_by_id(self, product_id: int) -> dict | None:
        """ Функция для получения товара по его id """
        values = await self.select_many("SELECT * FROM get_product_by_id($1);", product_id)
        if len(values) == 0:
            return None
        product = values[0]
        product["variants"] = await self.select_many("SELECT * FROM product_get_variants($1);", product_id)
        return product

    
    async def get_products(self, order_by: str | None, page: int | None, per_page: int | None, min_price: int | None, max_price: int | None, collection_ids: list[int] | list, category_ids: list[int] | list, options: list[str] | list) -> list | None:
        """Функция для выдачи товаров с фильтрами и сортировкой """
        statement = self.statement_sort("SELECT * FROM get_products($1, $2, $3, $4, $5);",
                                   order_by, page, per_page)

        products = await self.select_many(statement, min_price, max_price, collection_ids, category_ids, options)
        if len(products) == 0:
            return []
        
        product_ids = [p["id"] for p in products]
        variants = await self.select_many("SELECT * FROM product_get_variants_by_ids($1);", product_ids)

        for product in products:
            product["variants"] = [v for v in variants if v["product_id"] == product["id"]]

        return products
    
    async def get_products_filters(self, min_price: int = None, max_price: int = None, collection_ids: list[int] = [], category_ids: list[int] = [], options: list[str] = []) -> dict:
        """Функция для выдачи какие фильтры доступны в данной выборке """
        statement = "SELECT * FROM get_filter_info_by_product_ids(ARRAY(SELECT id FROM get_products($1::int, $2::int, $3::int[], $4::int[], $5::text[])));"
        values = await self.select_many(statement, min_price, max_price, collection_ids, category_ids, options)
        info = dict()
        for value in values:
            info[value["name"]] = value["values"]
        for k in ["collection_ids", "category_ids"]:
            try:
                info[k] = list(map(int, info[k]))
            except:
                info[k] = None
        try:
            info["min_and_max_price"] = list(map(float, info["min_and_max_price"]))
        except:
            info["min_and_max_price"] = None
        return info


    async def update_products(self, products: list):
        """
        Функция для добавления/обновления товаров. Обновляет таблицы: 
        product, image, product2property, variant, variant2option_value, collection2product
        """ 
        await self._update_products(products)
        await self._update_collection2product(products)
        await self._update_product2property(products)
        await self._update_images(products)
        await self._update_variants(products)
        await self._update_variant2option_value(products)

    async def _update_products(self, products):
        columns = ("id", "category_id", "created_at", "updated_at", "is_hidden", "available", 
                   "archived", "canonical_url_collection_id", "unit", "ignore_discounts", "title", "description", "currency_code")
        values = [(c["id"], c["category_id"], parse_timestamp(c["created_at"]), parse_timestamp(c["updated_at"]), 
                   c["is_hidden"], c["available"], c["archived"], c["canonical_url_collection_id"], c["unit"], c["ignore_discounts"], 
                   c["title"], parse_html(c["description"]), c["currency_code"]) for c in products]
        await self.execute_many("product", columns, values)
    
    async def _update_collection2product(self, products):
        columns = ("collection_id", "product_id")
        values = [(c, p["id"]) for p in products for c in p["collections_ids"]]
        await self.execute_many("collection2product", columns, values)
    
    async def _update_product2property(self, products):
        columns = ("property_id", "product_id", "value", "position")
        values = [(c["property_id"], p["id"], c["title"], c["position"]) for p in products for c in p["characteristics"]]
        await self.execute_many("product2property", columns, values)

    async def _update_images(self, products):
        columns = ("id", "product_id", "position", "original_url")
        values = [(i["id"], p["id"], i["position"], i["original_url"]) for p in products for i in p["images"]]
        await self.execute_many("image", columns, values)

    async def _update_variants(self, products):
        columns = ("id", "title", "product_id", "sku", "available", "image_id", "weight",
                   "quantity", "quantities_at_warehouses", "cost_price", "cost_price_in_site_currency",
                   "price_in_site_currency", "base_price", "old_price", "price", 
                   "base_price_in_site_currency", "old_price_in_site_currency")
        values = [(v["id"], v["title"], v["product_id"], v["sku"], v["available"], v["image_id"], parse_null_float(v["weight"]),
                   v["quantity"], parse_quantity_at_warehouses(v), parse_null_float(v["cost_price"]), parse_null_float(v["cost_price_in_site_currency"]),
                   parse_null_float(v["price_in_site_currency"]), parse_null_float(v["base_price"]), parse_null_float(v["old_price"]), parse_null_float(v["price"]), 
                   parse_null_float(v["base_price_in_site_currency"]), parse_null_float(v["old_price_in_site_currency"])) for p in products for v in p["variants"]]
        await self.execute_many("variant", columns, values)

    async def _update_variant2option_value(self, products):
        columns = ("variant_id", "option_value_id")
        values = [(v["id"], o["id"]) for p in products for v in p["variants"] for o in v["option_values"]]
        await self.execute_many("variant2option_value", columns, values)


    # ==== properties ====

    async def get_properties(self):
        """ Получение всех свойств """
        return await self.select_many("SELECT * FROM property;")

    async def update_properties(self, properties: list):
        """ Функция для добавления/удаления новых значений опций """
        columns = ("id", "position", "is_hidden", "is_navigational", "title")
        values = [(c["id"], c["position"], c["is_hidden"], c["is_navigational"], c["title"]) for c in properties]
        await self.execute_many("property", columns, values)


    # ==== option_values ====

    async def update_option_values(self, option_values: list):
        """ Функция для добавления/удаления новых значений опций """
        columns = ("id", "option_name_id", "position", "value", "image_url")
        values = [(c["id"], c["option_name_id"], c["position"], c["title"], c["image_url"]) for c in option_values]
        await self.execute_many("option_value", columns, values)


    # ==== option_names ====

    async def get_option_names(self):
        """ Получение всех свойств """
        return await self.select_many("SELECT * FROM option_name;")

    async def update_option_names(self, option_names: list):
        """ Функция для добавления/удаления новых имен опций """
        columns = ("id", "position", "navigational", "title")
        values = [(c["id"], c["position"], c["navigational"], c["title"]) for c in option_names]
        await self.execute_many("option_name", columns, values)


    # ==== categories ====

    async def get_category_by_id(self, category_id) -> dict | None:
        """ Функция для получения категории по ее id """
        values = await self.select_many("SELECT * FROM get_category_by_id($1);", category_id)
        return values[0] if len(values) > 0 else None
    
    async def get_category_by_title(self, category_title) -> dict | None:
        """ Функция для получения категории по ее title """
        values = await self.select_many("SELECT * FROM get_category_by_title($1);", category_title)
        return values[0] if len(values) > 0 else None
    
    async def get_categories(self, excluded_titles) -> list:
        """ Функция для получения категории по ее id """
        values = await self.select_many("SELECT * FROM get_categories($1);", excluded_titles)
        return values

    async def update_categories(self, categories: list):
        """ Функция для добавления новых коллекций. Если коллекция с таким id есть, то идет обновление ее полей """
        columns = ("id", "parent_id", "title", "position")
        values = [(c["id"], c["parent_id"], c["title"], c["position"]) for c in categories]
        await self.execute_many("category", columns, values)


    # ==== collections ====

    async def get_collection_by_id(self, collection_id) -> dict | None:
        """ Функция для получения категории по ее id """
        values = await self.select_many("SELECT * FROM get_collection_by_id($1);", collection_id)
        return values[0] if len(values) > 0 else None
    
    async def get_collection_by_title(self, collection_title) -> dict | None:
        """ Функция для получения категории по ее title """
        values = await self.select_many("SELECT * FROM get_collection_by_title($1);", collection_title)
        return values[0] if len(values) > 0 else None
    
    async def get_collections(self, excluded_titles) -> list:
        """ Функция для получения категории по ее id """
        values = await self.select_many("SELECT * FROM collection")
        return values
    async def update_collections(self, collections: list):
        """ Функция для добавления новых коллекций. Если коллекция с таким id есть, то идет обновление ее полей """
        columns = ("id", "parent_id", "title", "description", "position", "is_hidden", "is_smart")
        values = [(c["id"], c["parent_id"], c["title"], parse_html(c["seo_description"]), c["position"], c["is_hidden"], c["is_smart"]) for c in collections]
        await self.execute_many("collection", columns, values)

 
    # ==== tools ====

    async def connect(self):
        """ Открытие соединения с бд """
        self.conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        self.is_connected = True

    async def close_connection(self):
        """ Закрытие соединения с бд """
        await self.conn.close()
        self.is_connected = False

    async def execute_one(self, statement: str, *args, start: bool = True, close: bool = True) -> list[dict] | None:
        """ Выполнение одной операции """
        return await self.select_many(statement, *args, start=start, close=close)

    async def execute_many(self, table_name: str, columns: tuple[str], values: list, start: bool = True, close: bool = True) -> None:
        """ Функция для вставки/обновления нескольких строчек """
        if start:
            await self.connect()

        await self.conn.executemany(self.get_insert_or_update_statement(table_name, columns), values)

        if close:
            await self.close_connection()

    async def select_many(self, statement: str, *args, start: bool = True, close: bool = True) -> list[dict]:
        """ Функция для получения значений по введенному sql запросу """
        if start:
            await self.connect()
        
        records = await self.conn.fetch(statement, *args)

        if close:
            await self.close_connection()

        values = [dict(record) for record in records]
        return values

    def get_insert_or_update_statement(self, table_name: str, columns: tuple[str]) -> str:
        """ Функия для создания sql запроса на добавление/обновление данных в таблице """
        if not self.is_table_name(table_name):
            raise NameError("Invalid table name")
        column_with_quotes = [self.quotes_to_name(c) for c in columns]
        column_names = ", ".join(column_with_quotes)
        dollars = ", ".join([f"${i + 1}" for i in range(len(columns))])
        statement = f"INSERT INTO {table_name} ({column_names}) VALUES "
        statement += f"({dollars}) ON CONFLICT (id) DO UPDATE SET"
        statement += ", ".join([f"{c} = EXCLUDED.{c}" for c in column_with_quotes]) + ", db_hidden = FALSE;"
        return statement
    
    def quotes_to_name(self, name: str) -> str:
        """ Добавляет двойные кавычки к имени """
        return f"\"{name}\""

    def is_table_name(self, name: str) -> bool:
        """ Функция для валидации имени таблицы, не содержит ли оно лишних символов """
        return not any([c in name for c in EXCLUDED_CHARACTERS])

    def statement_sort(self, statement: str, order_by: str = None, page: int = None, per_page: int = None) -> str:
        """ 
        Функция, которая добавляет сортировку по определенной колонке sql запросу.
        Если перед названием колонки будет стоять минус, то сортировка будет по убыванию:
        order_column = "title"   по возрастанию
        order_column = "-title"  по убыванию
        """
        if statement[-1] == ";": statement = statement[:-1]
        
        if order_by is not None:
            ascending = True
            if order_by[0] == "-":
                order_by = order_by[1:]
                ascending = False
            if not self.is_table_name(order_by):
                raise NameError("Invalid column name")
            statement += f" ORDER BY {self.quotes_to_name(order_by)}"
            statement += " ASC" if ascending else " DESC" 

        if page is not None and per_page is not None:
            statement += f" LIMIT {per_page} OFFSET {page - 1} * {per_page}"

        statement += ";"
        return statement




    
    async def registration(self, name, surname, phone, email, birth_date, password): # Добавляем нового пользователя магазина
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name, port=self.port)
        records = await conn.fetch('SELECT * FROM customers WHERE email = $1', email)

        values = [dict(record) for record in records]
        if values and len(values) > 0:
            return False
            
        password = await token_process.encrypt_string(password)
        email_accept = 'Unverified'
        phone_accept = 'Unverified'

        await conn.execute('''INSERT INTO customers
        (name, surname, phone, email, birth_date, password, email_accept, phone_accept)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8);''', name, surname, phone, email, birth_date, password, email_accept, phone_accept)

        await conn.close()
        return True
    
    async def accept_email(self, email): # Добавляем нового пользователя магазина
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name, port=self.port)
        await conn.execute('''UPDATE collections SET email_accept = $1 WHERE email = $2;''', 'Verified', email)
        await conn.close()
        return True
    
    async def accept_phone(self, email): # Добавляем нового пользователя магазина
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name, port=self.port)
        await conn.execute('''UPDATE collections SET phone_accept = $1 WHERE email = $2;''', 'Verified', email)
        await conn.close()
        return True
    
    async def delete_profile(self, email): # Удаление пользователя из БД
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name, port=self.port)
        try:
            await conn.execute('''DELETE from customers WHERE email = $1;''', email)
            await conn.close()
            print('Information deleted')
            return True
        except: 
            print('Возникла ошибка. В процессе удалени пользователя')
            return False
    
    async def login(self, email, password): 
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name, port=self.port)
        records = await conn.fetch('SELECT password FROM customers WHERE email = $1', email)
        await conn.close()
        values = [dict(record) for record in records]
        #print(values[0]['password'])

        if not values or len(values) == 0:
            print('Incorrect data recieving')
            return False
        
        # TODO Заменить на блок отлавливания ошибок

        if password == await token_process.decrypt_string(values[0]['password']):
            return True
        else:
            return False
    
    async def find_user(self, email):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('SELECT * FROM customers WHERE email = $1', email)
        await conn.close()
        values = [dict(record) for record in records]
        return values[0]
    
    async def get_category_id_by_title(self, title):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('SELECT insales_id FROM collections WHERE title = $1', title)
        await conn.close()
        values = [dict(record) for record in records]
        return values[0]['insales_id']
    
    async def get_category_by_title(self, title):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('SELECT insales_id FROM collections WHERE title = $1', title)
        await conn.close()
        values = [dict(record) for record in records]
        #print(values[0]['password'])
        return values[0]
    
    async def get_product_list(self):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('SELECT * FROM products;')
        await conn.close()
        values = [dict(record) for record in records]
        #print(values[0]['password'])
        return values
        #return values[0]['insales_id']
    
    async def get_all_users(self):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('SELECT * FROM customers;')
        await conn.close()
        values = [dict(record) for record in records]
        return values[0]
    
    async def get_all_collections(self):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('SELECT * FROM collections;')
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_all_products_from_category_title(self, title): # by title
        category_id = await self.get_category_id_by_title(title) # Выдает insales id
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('''SELECT * FROM products WHERE category_id = $1;''', category_id)
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_all_products_from_category_id(self, category_id): # by id
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('''SELECT * FROM products WHERE category_id = $1;''', category_id)
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_product_by_title(self, title):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('''SELECT * FROM products WHERE title = $1;''', title)
        await conn.close()
        values = [dict(record) for record in records]
        return values[0]
    
    async def get_category_title_and_id_by_product_id(self, produc_id):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('''SELECT category_id FROM products WHERE insales_id = $1;''', produc_id)
        values_id = [dict(record) for record in records]
        records = await conn.fetch('''SELECT title FROM collections WHERE insales_id = $1;''', int(values_id[0]['category_id']))
        await conn.close()
        values_title = [dict(record) for record in records]
        return values_id[0], values_title[0]

    
    async def add_collections(self, insales_id, parent_id, title, description):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        await conn.execute('''INSERT INTO collections (insales_id, parent_id, title, description) VALUES ($1, $2, $3, $4);''', insales_id, parent_id, title, description)
        await conn.close()
        return True
    
    async def add_to_wishlist(self, email, insales_id):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        try:
            await conn.execute("""
            INSERT INTO wishlist (customer_id, product_id) VALUES
            ((SELECT id FROM customers WHERE email = $1), 
            (SELECT id FROM products WHERE insales_id = $2));
            """, email, insales_id)
            return True
        except:
            return False
        finally:
            conn.close()
    
    async def update_profile_info(self, email, name, surname, middlename, city, username):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        if name != '':
            await conn.execute('''UPDATE customers SET name = $1 WHERE email = $2;''', name, email)
        if surname != '':
            await conn.execute('''UPDATE customers SET surname = $1 WHERE email = $2;''', surname, email)
        if middlename != '':
            await conn.execute('''UPDATE customers SET middlename = $1 WHERE email = $2;''', middlename, email)
        if city != '':
            await conn.execute('''UPDATE customers SET city = $1 WHERE email = $2;''', city, email)
        if username != '':
            await conn.execute('''UPDATE customers SET name = $1 WHERE email = $2;''', username, email)
        await conn.close()
        return True
    
    async def update_profile_email(self, email, new_email):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        await conn.execute('''UPDATE customers SET email = $1 WHERE email = $2;''', new_email, email)
        await conn.close()
        return True
    
    async def update_profile_phone(self, email, phone):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        await conn.execute('''UPDATE customers SET phone = $1 WHERE email = $2;''', phone, email)
        await conn.close()
        return True
    
    async def delete_from_wishlist(self, email, insales_id):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch("""
            SELECT COUNT(*) FROM 
                wishlist w JOIN customers c ON w.customer_id = c.id
                JOIN products p ON w.product_id = p.id
                WHERE c.email = $1 AND p.insales_id = $2;
            """, email, insales_id)
        values = dict(records[0])
        await conn.execute("""
            DELETE FROM 
                wishlist w
            USING 
                customers c,
                products p
            WHERE 
                w.customer_id = c.id AND w.product_id = p.id
                AND c.email = $1 AND p.insales_id = $2;
            """, email, insales_id)
        await conn.close()
        # Проверка (True/False), был ли удален товар или такого не нашлось
        return values["count"] > 0


    async def update_products(self, product):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        await conn.execute('''INSERT INTO products 
                                (id, available, category_id, material, colour, brand, size, price, title, description, variants_id, collections_ids, images)
                              VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13);''',product['id'], product['available'], product['category_id'],
                              product['material'], product['colour'], product['brand'], str(product['size']), product['price'],
                              product['title'], product['description'], product['variants'], product['collections_ids'], product['images'])
                              
        await conn.close()
        return True

        '''
        UPDATE
                              SET available = $12, category_id = $13, material = $14, colour = $15,
                              brand = $16, size = $17, price = $18, description = $19, insales_id = $20, title = $21, images = $22;

                              product['available'], product['category_id'], product['material'], product['colour'], product['brand'],
                              str(product['size']), product['price'], product['description'], product['insales_id'], product['title'], product['images'])
        '''
    
    async def update_collections(self, insales_id, parent_id, title, description):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        await conn.execute('''INSERT INTO collections (insales_id, parent_id, title, description)
                              VALUES ($1, $2, $3, $4) ON CONFLICT (isales_id) DO
                              UPDATE SET isales_id = $5, parent_id = $6, title = $7, description = $8;''',
                              insales_id, parent_id, title, description, insales_id, parent_id, title, description)
        await conn.close()
        print('Information added')
        return True
    
    async def add_new_order(self, customer, date, summ):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        await conn.execute('''INSERT INTO orders (customer, date, summ) VALUES ($1, $2, $3);''', customer, date, summ)
        await conn.close()
        print('Information added')
        return True
    
    async def get_all_orders(self):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.execute('''SELECT * FROM orders;''')
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_wishlist_products(self, email):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('''SELECT p.id, available, category_id, material, colour, brand, 
                                            size, price, description, insales_id, title, variants_id, collection_ids, images FROM 
                                        wishlist w JOIN customers c ON w.customer_id = c.id AND c.email = $1
                                        JOIN products p ON w.product_id = p.id;''', email)
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_product_from_db_byid(self, product_id):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('''SELECT * FROM products WHERE id = $1;''', product_id)
        await conn.close()
        values = [dict(record) for record in records]
        print(values)
        return values[0]
    
    async def get_collections_id_from_db(self):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name, port=self.port)
        records = await conn.fetch("SELECT * FROM collection")
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_collection_by_id(self, collection_id):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('''SELECT * FROM collections WHERE insales_id = $1;''', collection_id)
        await conn.close()
        values = [dict(record) for record in records]
        return values[0]
    
    async def check_collections_from_product(self, collection_id):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name,port=self.port)
        records = await conn.fetch('''SELECT * FROM products WHERE $1 = ANY(collections_ids)''', collection_id)
        await conn.close()
        values = [dict(record) for record in records]
        return values


    # ==== Работа с url изображениями ==== 
    # async def add_all_images(self, images: list) -> None:
    #     conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)

    #     try:
            
    #     except:
    #         raise   


        

    





