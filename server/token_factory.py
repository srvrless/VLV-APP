from datetime import datetime, timedelta
from server_exceptions import EmptyDataError, TokenValidationError
import json
from cryptography.fernet import Fernet
import asyncio
from decorate import Decorate
from quart import jsonify
# Production of tokens for users



token_decorate = Decorate()



class EncryptingService:
    def __init__(self):
        return
    
    async def create_key(self):
        key = Fernet.generate_key()
        with open('crypto.key', 'wb') as key_file:
            key_file.write(key)
    
    async def load_key(self):
        # Загружаем ключ 'crypto.key' из текущего каталога
        return await open('crypto.key', 'rb').read()
    
    async def encrypt_phrase(self, my_str):
        key = self.load_key()
        f = Fernet(key)
        token = await f.encrypt(my_str.encode())
        return token
    
    async def decrypt_phrase(self, token):
        key = self.load_key()
        f = Fernet(key)
        decrypted_data = await f.decrypt(token)
        return decrypted_data.decode()
    
    async def email_from_token(self, token):
        return self.read(token).get('email')
    
    async def expiration_data_from_token(self, token):
        return self.read(token).get('expiration_date')


class Access(EncryptingService):
    def __init__(self):
        return
    
    async def create_access_token(self, email): 
        return {
            'code': 200,
            'acess_token': self.encrypt_phrase(json.dumps(
                {
                    'email': email, # по конкретной почте создается токен
                    'start_date': datetime.now().isoformat(),
                    'expiration_date': (datetime.now() + timedelta(days=1)).isoformat() # создается на 24 часа
                }))
            } 
    
    async def validate_access_token(self, access_token):

        try: 
            email = await self.email_from_token(access_token)
        except:
            raise Exception('Не удалось корректно расшифровать токен, либо email в нем отсутствует.')

        if email is None: # Отправляется при ошибочной обработке функции и неполучении email из присланного токена. 
            return {
                'code': 403,
                'message': 'Нельзя прочитать токен, либо email отсутствует. Требуется повторная авторизация'
            }

        differ = datetime.fromisoformat(self.expiration_data_from_token(access_token)) - datetime.now()

        if differ.total_seconds() > 0:

             return {
                'code': 200,
                'message': 'Токен действителен. Доступ открыт'
                 }

        else: 
            return {
                'code': 405,
                'message': 'Время действия токена уже истекло. Трубется обновление acess_token с помощью refresh_token'
                }



class Refresh(Access):
    def __init__(self):
        return
    
    async def create_refresh_token(self, email): # Creating new refresh tokenn for user.
        # It will be awailable for 7 days

        try: 
            if not email or email == None: # проверка на то, был ле передан почтовый адрес. Без него не получится сделать рефреш
                raise EmptyDataError('No email data. Cant create token') # выброс кастомной ошибки
        except Exception as e:
            print('Error while combinig data in "create_refresh_token"') 

        return {
            'code': 200, #'access_token': self.create_access(email).decode(),
            'refresh_token': self.encrypt_phrase(json.dumps(
                {
                'email': email, # по конкретной почте создается токен
                'start_date': datetime.now().isoformat(),
                'expiration_date': (datetime.now() + timedelta(days=7)).isoformat() # время действия токена (одна неделя)
                })).decode()
            }
    
    #TODO Для создания повышенного уровня защиты, необходимо внедрить проверку на пользователя: Есть ли этот пользователь в БД или нет.
    async def validate_refresh_token(self, refresh_token):
        try: 
            email = await self.email_from_token(refresh_token)
        except:
            raise Exception('Не удалось корректно расшифровать токен, либо email в нем отсутствует. ')
        # email_from_params = await database.find_user(email) # Проверяем на наличие такого пользователя # ! Такая проверка тут не нужна. Она лишняя при обычной защите
        # email_from_params = email_from_params['email']

        if email is None: # Отправляется при ошибочной обработке функции и неполучении email из присланного токена. 
            return {
                'code': 403,
                'message': 'Нельзя прочитать токен, либо email отсутствует.Требуется регистрация'
                }
        
        differ = datetime.fromisoformat(self.expiration_data_from_token(refresh_token)) - datetime.now()

        if differ.total_seconds() > 0:
            return {
                'code': 200,
                'message': 'Токен еще действителен. Не требуется его обновление',
                'new_access_token': self.create_access(email).decode()
                    }

        else:
            return {
                'code': 405,
                'message': 'Время действия токена уже истекло. Требуется создание нового refresh_token'
                }
        
    async def create_acess_by_refresh(self, refresh_token): # Создание нового acess_token для действующего рефреша. 
        result = await self.validate_refresh_token(refresh_token)

        if result('code') == 200:
            email = await self.email_from_token(refresh_token)
            
            return asyncio.run(self.create_access_token(email))
    
    
@token_decorate.refresh_decorator
async def refresh_validation(refresh_token):
    try:
        # refresh_token = request.headers['refresh_token']
        if refresh_token is None or refresh_token == '':
            return jsonify(
                {
                    'code': 402,
                    'message': 'Refresh token отсутствует. Запрос отклонен. Необходимо скорректировать запрос на сервер'
                }
            )
    
        result = await Refresh().validate_refresh_token(refresh_token)

        if result('code') == 200:
            return jsonify(
                {
                    'code': 200,
                    'message': 'Токен действителен.'
                }
            )
        
    except:
        raise TokenValidationError('Ошибка в декораторе или функции проверки данных токена')
    


@token_decorate.access_decorator
async def access_validation(access_token):
    try:
        # refresh_token = request.headers['refresh_token']
        if access_token is None or access_token == '':
            return jsonify(
                {
                    'code': 402,
                    'message': 'Access token отсутствует. Запрос отклонен. Необходимо скорректировать запрос на сервер'
                }
            )
    
        result = await Access().validate_access_token(access_token)

        if result('code') == 200:
            return jsonify(
                {
                    'code': 200,
                    'message': 'Токен действителен.'
                }
            )
        
    except:
        raise TokenValidationError('Ошибка в декораторе или функции проверки данных токена')