
import asyncpg
import json
from service import TokenProcess


token_process = TokenProcess()

class Database:
    
    def __init__(self):
        self.host = 'localhost'
        self.db_name = 'vlv_shop'
        self. dbuser = 'postgres'
        self.password = 'admin'
        return
    
    async def registration(self, name, email, password, city, billings, wishlist): # Добавляем нового пользователя магазина
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('SELECT * FROM customers WHERE email = $1', email)

        try:
            values = [dict(record) for record in records]
            if values and len(values) > 0:
                return False
        except Exception as e:
            print(e, 'Ошибка в процессе получения данных о зарегистрированных пользователях. Регистрация продолжается')
            
        password = await token_process.encrypt_string(password)
        email_accept = 'Unverified'
        phone_accept = 'Unverified'

        await conn.execute('''INSERT INTO customers
        (name, email, password, city, billing_history, wishlist, email_accept, phone_accept)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8);''', name, email, password, city, billings, wishlist, email_accept, phone_accept)

        await conn.close()
        return True
    
    async def accept_email(self, email): # Добавляем нового пользователя магазина
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        await conn.execute('''UPDATE collections SET email_accept = $1 WHERE email = $2;''', 'Verified', email)
        await conn.close()
        return True
    
    async def accept_phone(self, email): # Добавляем нового пользователя магазина
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        await conn.execute('''UPDATE collections SET phone_accept = $1 WHERE email = $2;''', 'Verified', email)
        await conn.close()
        return True
    
    async def delete_profile(self, email): # Удаление пользователя из БД
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        try:
            await conn.execute('''DELETE from customers WHERE email = $1;''', email)
            await conn.close()
            print('Information deleted')
            return True
        except: 
            print('Возникла ошибка. В процессе удалени пользователя')
            return False
    
    async def login(self, email, password): 
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
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
            return False #result = json.dumps(values).replace('\\', '')
    
    async def find_user(self, email):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('SELECT * FROM customers WHERE email = $1', email)
        await conn.close()
        values = [dict(record) for record in records]
        #print(values[0]['password'])
        return values[0]
    
    async def get_category_id_by_title(self, title):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('SELECT insales_id FROM collections WHERE title = $1', title)
        await conn.close()
        values = [dict(record) for record in records]
        return values[0]['insales_id']
    
    async def get_category_by_title(self, title):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('SELECT insales_id FROM collections WHERE title = $1', title)
        await conn.close()
        values = [dict(record) for record in records]
        #print(values[0]['password'])
        return values[0]
    
    async def get_product_list(self):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('SELECT * FROM products;')
        await conn.close()
        values = [dict(record) for record in records]
        #print(values[0]['password'])
        return values
        #return values[0]['insales_id']
    
    async def get_all_users(self):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('SELECT * FROM customers;')
        await conn.close()
        values = [dict(record) for record in records]
        return values[0]
    
    async def get_all_collections(self):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('SELECT * FROM collections;')
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_all_products_from_category_title(self, title): # by title
        category_id = await self.get_category_id_by_title(title) # Выдает insales id
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('''SELECT * FROM products WHERE category_id = $1;''', category_id)
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_all_products_from_category_id(self, category_id): # by id
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('''SELECT * FROM products WHERE category_id = $1;''', category_id)
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_product_by_title(self, title):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('''SELECT * FROM products WHERE title = $1;''', title)
        await conn.close()
        values = [dict(record) for record in records]
        return values[0]
    
    async def get_category_title_and_id_by_product_id(self, produc_id):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('''SELECT category_id FROM products WHERE insales_id = $1;''', produc_id)
        values_id = [dict(record) for record in records]
        records = await conn.fetch('''SELECT title FROM collections WHERE insales_id = $1;''', int(values_id[0]['category_id']))
        await conn.close()
        values_title = [dict(record) for record in records]
        return values_id[0], values_title[0]

    
    async def add_collections(self, insales_id, parent_id, title, description):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        await conn.execute('''INSERT INTO collections (insales_id, parent_id, title, description) VALUES ($1, $2, $3, $4);''', insales_id, parent_id, title, description)
        await conn.close()
        return True
    
    async def add_to_wishlist(self, email, product_id):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('''SELECT * FROM customers WHERE email = $1;''', email)
        values = [dict(record) for record in records]
        if len(values) > 0 and values[0]['wishlist'] is not None:
            wishlist = json.loads(values[0]['wishlist'])
            if type(wishlist) == int: # Всего один элемент
                wishlist = []
        else: 
            wishlist = []
        wishlist.append(product_id)
        await conn.execute('''UPDATE customers SET wishlist = $1 WHERE email = $2;''',json.dumps(wishlist), email)
        await conn.close()
        print('Information added')
        return True
    
    async def update_profile_info(self, email, name, surname, middlename, city, username):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
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
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        await conn.execute('''UPDATE customers SET email = $1 WHERE email = $2;''', new_email, email)
        await conn.close()
        return True
    
    async def update_profile_phone(self, email, phone):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        await conn.execute('''UPDATE customers SET phone = $1 WHERE email = $2;''', phone, email)
        await conn.close()
        return True
    
    async def delete_from_wishlist(self, email, product_id):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('''SELECT * FROM customers WHERE email = $1;''', email)
        values = [dict(record) for record in records]
        wishlist = json.loads(values[0]['wishlist'])
        wishlist.remove(product_id)
        await conn.execute('''UPDATE customers SET wishlist = $1 WHERE email= $2;''', json.dumps(wishlist), email)
        await conn.close()
        print('Information Deleted')
        return True


    async def update_products(self, product):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        await conn.execute('''INSERT INTO products (available, category_id, material, colour, brand, size, price, description, insales_id, title, images, variants_id, collection_ids)
                              VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13);''',product['available'], product['category_id'],
                              product['material'], product['colour'], product['brand'], str(product['size']), product['price'],
                              product['description'], product['insales_id'], product['title'], product['images'], product['variants'], product['collections_ids'])
                              
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
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        await conn.execute('''INSERT INTO collections (insales_id, parent_id, title, description)
                              VALUES ($1, $2, $3, $4) ON CONFLICT (isales_id) DO
                              UPDATE SET isales_id = $5, parent_id = $6, title = $7, description = $8;''',
                              insales_id, parent_id, title, description, insales_id, parent_id, title, description)
        await conn.close()
        print('Information added')
        return True
    
    async def add_new_order(self, customer, date, summ):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        await conn.execute('''INSERT INTO orders (customer, date, summ) VALUES ($1, $2, $3);''', customer, date, summ)
        await conn.close()
        print('Information added')
        return True
    
    async def get_all_orders(self):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.execute('''SELECT * FROM orders;''')
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_wishlist(self, email):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('''SELECT wishlist FROM customers WHERE email = $1;''', email)
        await conn.close()
        values = [dict(record) for record in records]
        if values[0]['wishlist'] is None:
            return []
        return values[0]['wishlist']
    
    async def get_product_from_db_byid(self, product_id):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('''SELECT * FROM products WHERE insales_id = $1;''', product_id)
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_collections_id_from_db(self):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('''SELECT insales_id FROM collections;''')
        await conn.close()
        values = [dict(record) for record in records]
        return values
    
    async def get_collection_by_id(self, collection_id):
        conn = await asyncpg.connect(host=self.host, user=self.dbuser, password=self.password, database=self.db_name)
        records = await conn.fetch('''SELECT * FROM collections WHERE insales_id = $1;''', collection_id)
        await conn.close()
        values = [dict(record) for record in records]
        return values

    





