


# Движок пользовательских сессий
#? Включает в себя абсолютно весь контроль пользовательких сессий. Нужен для правильной работы корзины. 
#? Все сессии хранятся в каталоге (catalog в json)


import json
from decorate import Decorate
from random import randint


file_decorator = Decorate()


@file_decorator.open_file_decorator
def get_data_fromfile():
    with open('sessions.json', 'r') as session_file:
        data = json.load(session_file)
        return data 


@file_decorator.close_file_decorator
def put_data_tofile(data):
    with open('sessions.json', 'w') as session_file:
        json.dumps(session_file, data)
        return True


class SSession:
    def __init__(self):
        self.default_structure = {
            'catalog': []
        }

        try:
            data = get_data_fromfile() # Получение данных
            
            if not data['catalog'] or len(data) == 0:
                data['catalog'] == self.default_structure
            
            if len(data['catalog']) == 0:
                data['catalog'].append({})
            
            put_data_tofile(data) # Запись 

        except Exception as e:
            print('Невозможно открыть файл с сессиями. Ошибка в самой функции инициализации. Необходимо проверить правильность работы с данным файлом.', e)


    async def create_session(self, email): # Создание новой сессии с 0. Просто добавляется необходимая структура для каждой сессии

        data = get_data_fromfile() # Получение данных
       
        data['catalog'][email] = {
           'session_id': randint(0, 1000000000000000000000000000),
           'logged_in': False,
           'cart': []
        }
       
        put_data_tofile(data) # Запись 
        return
    
    async def insert_into_cart(self, email, info):

        data = get_data_fromfile()
        data['catalog'][email]['cart'].append(info)
        put_data_tofile(data)
        return True
    
    async def delete_from_cart(self, email, info):

        data = get_data_fromfile()
        data['catalog'][email]['cart'].remove(info)
        put_data_tofile(data)
        return True
    
    async def delete_session(self, email):

        data = get_data_fromfile()
        data['catalog'].remove(data['catalog'][email])
        put_data_tofile(data)
        return True
    
    
    