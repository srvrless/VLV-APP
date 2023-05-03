from quart import jsonify
from token_factory import access_creation, refresh_validation
from bs4 import BeautifulSoup
import json


#* Обработка html описания при получении товаров и категорий 
def html_parser(html_document):
        try:
            soup = BeautifulSoup(html_document, 'html.parser')
            text = soup.get_text()
            text = text.replace('Описание', '').replace('  ', '')
            return text
        except TypeError: return ''


async def token_validate_process(result):
    if isinstance(result, bool):
        if result:
            return jsonify({
                'code': 200,
                'message': 'Authorization method passed successfully'
            })
        else:
            return jsonify({
                'code': 406,
                'message': 'General error while processing user token information'
            })
    else:
        code = result.get('code')
        if code == 401:
            return jsonify({
                'code': 405,
                'message': 'Need to reauthorize to update the pair'
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


# ? Данный метод можно смело применять при любом авторизованном запросе
async def token_process(access_token, refresh_token): # ? Функция, которая отвечает за проверку подленности токена
    # info = await request.get_json()
    result = await access_validation(access_token) 

    if result is not True:
        if not refresh_token or refresh_token == '' or len(refresh_token) == 0:
            return jsonify({
                    'code': 203,
                    'message': 'Необходимо передать в запрос refresh_token. Он должен быть ненулевой для того, чтобы проверка прошла необходимым образом'
                })
        result = await refresh_validation(refresh_token)

        if result is not True:
            return jsonify({
                    'code': 401,
                    'message': 'Доступ закрыт. Необходимо авторизоваться повторно для создание новой пары refresh-access'
                })
            
        else:
            new_access_token = await access_creation(access_token)
            return jsonify({
                    'code': 201,
                    'message': 'Рефреш-токен действителен. Необходимо обновить access_token',
                    'access_token': new_access_token
                })
        
    elif result:
        return True
    
    else:
        return False


class CitySearchEngine:
    def __init__(self):
        return
    
    def open_citieslist(self):
        with open('cities.json', 'r') as cities_file:
            data = json.load(cities_file)
            return data
