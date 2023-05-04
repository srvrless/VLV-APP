import json
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from quart import jsonify



class TokenProcess:
    def __init__(self):
        return
    
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
        return open('crypto.key', 'rb').read()
    
    async def encrypt_string(self, my_str):
        """
        Encrypts a string parameter `my_str` using a Fernet key and returns the encrypted string.
        """
        key = await self.load_key()
        fernet = Fernet(key)
        encrypted_string = fernet.encrypt(my_str.encode())
        return encrypted_string 
    
    async def decrypt_string(self, encrypted_str):
        """
        Decrypts a string parameter `encrypted_str` using a Fernet key and returns the decrypted string.
        """
        key = await self.load_key()
        fernet = Fernet(key)
        decrypted_string = fernet.decrypt(encrypted_str)
        return decrypted_string.decode()

    async def create_token(self, email, mode):
        """
        Коммент к функциии
        """
        if mode == 'refresh':
            refresh_token = await self.encrypt_string(json.dumps({
                'email': email, 
                'start_date': datetime.now().isoformat(),
                'expiration_date': (datetime.now() + timedelta(days=7)).isoformat()
            }))
            refresh_token = refresh_token.decode()

            return {'code': 200, 'refresh_token': refresh_token}
    
        elif mode == 'access':
            access_token = await self.encrypt_string(json.dumps({
                'email': email,  # remove the unnecessary newline character from here
                'start_date': datetime.now().isoformat(),
                'expiration_date': (datetime.now() + timedelta(days=1)).isoformat(),
            }))
            access_token = access_token.decode()
            return {'code': 200, 'access_token': access_token}
    
        return False

    async def get_email_from_token(self,token):
        """
        Given an encrypted token string, returns the email from the decrypted token.
        """
        decoded_token = await self.decrypt_string(token)
        return decoded_token.split(':')[0]

    async def validate_token(self, token):
        try:
            email = json.loads(await self.decrypt_string(token))['email']
        except:
            raise Exception('Не удалось корректно расшифровать токен, либо email в нем отсутствует.')
    
        if not email: 
            return {'code': 403, 'message': 'Ошибка при обработке токена. Возможно, необходима регистрация'}
    
        time_diff = datetime.fromisoformat(json.loads(await self.decrypt_string(token))['expiration_date']) - datetime.now()

        if time_diff.total_seconds() > 0: return True
        else: return False
 
    async def create_couple(self, email):
        refresh_token = await self.create_token(email, 'refresh')
        refresh_token = refresh_token['refresh_token']
        access_token = await self.create_token(email, 'access')
        access_token = access_token['access_token']
        return {'access_token': access_token, 'refresh_token': refresh_token}

async def create_acess_by_refresh(self, refresh_token): #? Необходимо передавать сюда refresh_token
    result = await self.validate_token(refresh_token)

    if result('code') == 200:
        email = await self.email_from_token(refresh_token)
    return await self.create_token(email, 'access')

async def token_validate_process(result):
    """
    Оценка результата проверки: (True / False). Проверяет конкретный ответ от функции проверки
    """
    if isinstance(result, bool):

        if result: return jsonify({'code': 200, 'message': 'Authorization method passed successfully'})
        else: return jsonify({'code': 406, 'message': 'General error while processing user token information'})

    else:
        code = result.get('code')
        if code == 401: return jsonify({'code': 405,'message': 'Need to reauthorize to update the pair'
            })
        elif code == 201:
            return jsonify({
                'code': 405,
                'message': 'Access with the new access_token generated is required',
                'new_access_token': result['access_token']
            })
        elif code == 203:
            return jsonify({
                'code': 405,
                'message': 'refresh_token is also required to authorize the method'
            })

async def token_process(self, access_token, refresh_token):
    """
    Функця проверки токенов. Передает result к дальнейшей проверки
    """
    result = await self.validate_token(access_token) 

    if result is not True:
        result = await self.validate_token(refresh_token)

        if result is not True:
            return jsonify({
                    'code': 401,
                    'message': 'Доступ закрыт. Необходимо авторизоваться повторно для создание новой пары refresh-access'
                })  
        else:
            new_access_token = await create_acess_by_refresh(refresh_token)
            return jsonify({
                    'code': 201,
                    'message': 'Рефреш-токен действителен. Необходимо обновить access_token',
                    'access_token': new_access_token
                })
        
    elif result: return True
    else:return False


        


    