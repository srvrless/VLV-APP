from datetime import datetime, timedelta
import json
from cryptography.fernet import Fernet
import asyncio
from decorate import Decorate
from quart import jsonify
# Production of tokens for users



token_decorate = Decorate()




# Custom Class for handle the exceptions. 



class EmptyDataError(Exception): # Класс ошики, которая возникает при недостатке данных, передаваемых в функцию
    def __init__(self,*args):
        if args:
            self.mmessage = args[0]
        else:
            self.mmessage = None
    
    def __str__(self):
        if self.message:
            return 'EmptyDataError, {0} '.format(self.message)
        else:
            return 'Important data missed. You should check the way of transmitting args to function'




class TokenValidationError(Exception): # Класс ошики, которая возникает при недостатке данных, передаваемых в функцию
    def __init__(self,*args):
        if args:
            self.mmessage = args[0]
        else:
            self.mmessage = None
    
    def __str__(self):
        if self.message:
            return 'TokenValidationError, {0} '.format(self.message)
        else:
            return 'Нельзя проверить токен по какой-либо причине. Необходимо скорректировать ваш запрос и/или проверить правильность вводимых данных.'


class EncryptingService:
    def __init__(self):
        pass
    
    async def generate_key(self):
        """
        Generates a Fernet key and saves it to a file named 'crypto.key'.
        """
        key = Fernet.generate_key()
        with open('server/server_helpers/crypto.key', 'wb') as key_file:
            key_file.write(key)
    
    async def load_key(self):
        """
        Loads a previously generated Fernet key from the file named 'crypto.key'.
        """
        return open('server/server_helpers/crypto.key', 'rb').read()
    
    async def encrypt_string(self, my_str):
        """
        Encrypts a string parameter `my_str` using a Fernet key and returns the encrypted string.
        """
        key = await self.load_key()
        fernet = Fernet(key)
        encrypted_string = fernet.encrypt(my_str.encode())
        # return encrypted_string.decode()
        return encrypted_string #! может так получиться, что пароли шифруются так, а токены иначе
    
    async def decrypt_string(self, encrypted_str):
        """
        Decrypts a string parameter `encrypted_str` using a Fernet key and returns the decrypted string.
        """
        key = await self.load_key()
        fernet = Fernet(key)
        decrypted_string = fernet.decrypt(encrypted_str) #! тут может быть ошибка. Пока точно не понятно, как программа работает с входящими данными
        return decrypted_string.decode()
    
    async def get_email_from_token(self, token):
        """
        Given an encrypted token string, returns the email from the decrypted token.
        """
        decoded_token = await self.decrypt_string(token)
        return decoded_token.split(':')[0]
    
    async def get_expiration_date_from_token(self, token):
        """
        Given an encrypted token string, returns the expiration date from the decrypted token.
        """
        decoded_token = await self.decrypt_string(token)
        return decoded_token.split(':')[1]



class Access(EncryptingService):
    def __init__(self):
        super().__init__()  # you need to call the parent class' constructor
    
    async def create_access_token(self, email):
        try:
            access_token = await self.encrypt_string(
                json.dumps({
                    'email': email,  # remove the unnecessary newline character from here
                    'start_date': datetime.now().isoformat(),
                    'expiration_date': (datetime.now() + timedelta(days=1)).isoformat(),
                })
            )
            access_token = access_token.decode()
            return {
                'code': 200,
                'message': 'Access_token создан успешно.',
                'access_token': access_token,
            }
        except Exception as e:
            return {
                'code': 404,
                'message': f'Произошла ошибка при формировании access_token. Необходимо обратить внимание на функцию создания аксесс. Ошибка: {e}',
            }
    
    async def validate_access_token(self, access_token):
        try:
            email = json.loads(await self.decrypt_string(access_token))['email']  # extract 'email' from the access_token
        except:
            raise Exception('Не удалось корректно расшифровать токен, либо email в нем отсутствует.')
        if not email: 
            return {
                'code': 403,
                'message': 'Не удалось получить email из access_token. Необходимо повторно авторизоваться',
            }
        time_diff = datetime.fromisoformat(json.loads(await self.decrypt_string(access_token))['expiration_date']) - datetime.now()  # extract 'expiration_date' from the access_token
        if time_diff.total_seconds() > 0:
            return {
                'code': 200,
                'message': 'Токен действителен. Доступ открыт',
            }
        else:
            return {
                'code': 405,
                'message': 'Время действия токена уже истекло. Требуется обновление access_token с помощью refresh_token',
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
        

        refresh_token = await self.encrypt_string(json.dumps(
                {
                'email': email, # по конкретной почте создается токен
                'start_date': datetime.now().isoformat(),
                'expiration_date': (datetime.now() + timedelta(days=7)).isoformat() # время действия токена (одна неделя)
                }))
        refresh_token = refresh_token.decode()

        return {
            'code': 200, #'access_token': self.create_access(email).decode(),
            'refresh_token': refresh_token
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
            return True
        else:
            return jsonify(
                {
                    'code': 402,
                    'message': 'Токен недействителен'
                }
            )
        
    except:
        raise TokenValidationError('Ошибка в декораторе или функции проверки данных токена')
    


from functools import wraps

def access_decorator(func):
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token is None or access_token == '':
            return jsonify(
                        {
                            'code': 402,
                            'message': 'Access token отсутствует. Запрос отклонен. Необходимо скорректировать запрос на сервер'
                        }
                    )

        result = await Access().validate_access_token(access_token)

        if result['code'] == 200:
            return await func(request, *args, **kwargs)
        else:
            return jsonify(
                {
                    'code': 402,
                    'message': 'Токен недействителен'
                }
            )    
    return wrapper

@access_decorator
async def access_validation(request):
    try:
        return True
    except:
        raise TokenValidationError('Ошибка в декораторе или функции проверки данных токена')




@token_decorate.access_decorator
async def access_creation(old_access_token):
    try:
        email = await Refresh().email_from_token(old_access_token)
        info = await Refresh().create_access_token(email)
        if info('code') == 200:
            access_token = info('access_token')
            return jsonify(
                {
                    'code': 200,
                    'access_token': access_token
                }
            )
        
        elif info('code') == 404:
            return jsonify(
                {
                    'code': 404,
                    'message': 'Ошибка при генерации access_token'
                }
            )
    
    except Exception as e:
        return jsonify(
            {
                'code': 405,
                'message': 'Общая ошибка при выполнении функции создания токена; Ошибка декоратора. Тест: {}'.format(e)
            }
        )
    
@token_decorate.token_service_decorator
async def decrypt_and_get_email(token):
    return await EncryptingService().email_from_token(token)



async def create_couple_by_email(email):
    refresh_token = await Refresh().create_refresh_token(email)
    refresh_token = refresh_token['refresh_token']
    access_token = await Refresh().create_access_token(email)
    access_token = access_token['access_token']

    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

