from quart import Quart
from quart import jsonify
from quart import request
from quart import render_template
from server_helpers.session_factory import SSession
from server_helpers.token_factory import access_validation, refresh_validation, decrypt_and_get_email, access_creation, create_couple_by_email
from database import Database
from quart import abort
from bs4 import BeautifulSoup
import json
import requests



app = Quart(__name__)

ssession = SSession()
database = Database()
insales_url = 'https://26c60c2c500a6c6f1af7aa91d11c197c:a5f07ba6e0c4738819d1ba910731db57@myshop-bte337.myinsales.ru/admin'

'''
1 мая 2023

#? 1. Телефон добавляется в БД только после его подтверждения. До этого не стоит его добавлять в БД вообще.
- Таким образом, сначала регистрируем пользователя по его email, его имя и фамилию. 
- Потом туда уже будем добавлять его Имя, Фамилию и тд. 

#? 2. контроль заказов.
Для того, чтобы правильно контролировать заказы, нужно создать для этого отдельную таблицу.

'''

# TODO Добавлеие новых баннеров в БД
# TODO Вывод товаров из БД, чтобы их отображать на странице
#TODO Проверка, чтобы администратор был авторизован: Защита от перехода поперек пользовательского сценария
#TODO Добавление нового баннера / редактирование тех баннеров, которые есть сейчас на странице
# TODO: Вставить в программный код места, где создаются новые сессии и они управляются
# TODO: Сделать автоматическую выдачу токена при проверке рефреш, если рефреш еще действует (сейчас в ручном)
# TODO: В базу данных каждоо пользователя добавить поле "История заказов".
    ##? Добавить отдельный параметр вывода заказов, которые были когда-либо связаны с профилем (отдельный счетчик)
    ##? Вставить в программный код все, что касается истории заказов пользователя

# TODO: Каждому пользователю добавить поле, в котором будет содердаться информация о текущих его заказах.
    # Это должна быть отдельная таблица, в которой все это будет обрабатываться. Чтобы всю 
    # информацию можно было бы оттуда брать. И выдвать на экране


#TODO: сделать метод смены электронной почты с подтверждением через письмо также, как и было при регистрации
#TODO: сделать метод подтверждения номера телефона через смс, как и положено ----> подключиь для этого сторонний смс сервис
#TODO: Сделать метод удаления профиля
#TODO: написать функцию смены пароля и подтверждение данного действия через смс.
#TODO: Сделать таблицу отдельную, в которой будет список магазинов
#TODO Нужно нажать на кнопку на почте, чтобы ее подтвердить. 
#TODO Записать в БД статус электронной почты (код)
# TODO Отправка уведомдения о том, что код был неверный (если его ввели неверно)


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



def html_parser(html_document):
        try:
            soup = BeautifulSoup(html_document, 'html.parser')
            text = soup.get_text()
            text = text.replace('Описание', '')
            text = text.replace('  ', '')
            return text
        except TypeError: return ''


### Start app. Configuration parametres. ###


@app.route('/')
def index():
    return jsonify(
        {
            'code': 200,
            'message': 'Start'
        }
    )

@app.route('/update_coll_db', methods=['GET', 'POST']) #? Обновления категорий в БД
async def update_collections_in_database():
    if request.method == 'GET':

        info = requests.get(insales_url + '/' + 'collections.json').json()
        for i in info:
            result = await database.add_collections(i['id'], i['parent_id'], i['title'], str(i['position']))
            if result:
                pass
            else:
                abort(405) #? Не получилось добавить ту или иную коллекцию
        
        return jsonify(
            {
                'code': 200,
                'message': 'Все коллекции успешно добавлены'
            }
        )

@app.route('/update_prod_db', methods=['GET'])
async def update_products_in_database():
    if request.method == 'GET':

        box_variants = []
        material, colour, brand, size, price, images = '', '', '', '', '', []
        for page in range(1, 201):
            info = requests.get(insales_url + '/' + 'products.json', params={'page_sise': 100, 'page': page}).json()
            for product in info:
                for img in product.get('images', []):
                    images.append(img.get('original_url'))

                for characteristic in product.get('characteristics', []):
                    if characteristic.get('property_id', None) == 40865551: # Материал
                        material = characteristic.get('title', '')
                    elif characteristic.get('property_id', None) == 37399009: # Цвет
                        colour = characteristic.get('title', '')
                    elif characteristic.get('property_id', None) == 35926723: # Бренд
                        brand = characteristic.get('title', '')
                    elif characteristic.get('property_id', None) == 35932191: #? Размер
                        size = characteristic.get('title', '')

                if size:
                    size = [s.replace(' ', '') for s in size.split(',')]
                    try:
                        size = [float(s) for s in size]
                    except:
                        pass

                product_data = {
                    'available': str(product.get('available', False)),
                    'category_id': product.get('category_id', 0),
                    'material': material or '',
                    #'ads_category': product.get('characteristics', [])[0].get('title'),
                    'colour': colour or '',
                    'brand': brand or '',
                    'size': size or [],
                    'price': int(float(product.get('variants', [])[0].get('base_price', 0))), 
                    'description': html_parser(product.get('description', '')),
                    'insales_id': product.get('id', 0),
                    'title': product.get('title', ''),
                    'variants': [variant.get('id', 0) for variant in product.get('variants', [])],
                    'images': json.dumps(images) or '[]'
                }

                images = []
                result = await database.update_products(product_data)
        
        return jsonify({
            'code': 200,
            'message': 'All products were successfully updated in the database.'
            })

    return jsonify({'code': 405,
        'message': 'The method specified in the request is not allowed for the resource identified by the request URI.'
        })



@app.route('/product_list', methods=['GET', 'POST']) #? Получение списка товаров из БД
async def get_product_list():
    if request.method == 'GET':

        result = await database.get_product_list()

        return jsonify({
            'code': 200,
            'message': result
            })

    return jsonify({
        'code': 202,
        'message': 'Данный метод не поддерживается'
            })

@app.route('/collections_list', methods=['GET', 'POST']) #? Получение полного списка rколлекций из БД
async def get_collections_list():
    if request.method == 'GET':

        result = await database.get_all_categories()

        return jsonify({
            'code': 200,
            'message': result
            })

    return jsonify({
        'code': 202,
        'message': 'Данный метод не поддерживается'
            })

### Авторизация ###
# ? Алгоримт входа пользователя в приложение. Проверка его токенов. 


@app.route('/login', methods=['POST'])
async def login():

    if request.method == 'POST':
        info = await request.get_json()
        email = info['email']
        password = info['password']

        if await database.login(email, password):

            result = await create_couple_by_email(email)

            return jsonify({
                    'code': 200,
                     'message': 'Авторизация успешна. Для пользователя была сформирована новая пара токенов для обслуживания',
                    'access_token': result['access_token'],
                    'refresh_token': result['refresh_token']
                })
        
        else: 
            return jsonify({
                    'code': 400,
                    'message': 'Доступ закрыт. Возможно, неправильно введены данные пользователя для входа. Перепроверьте вводимые данные'
                })
    else:
        abort(400)

        
### Конец авторизации пользователя ###


### Регистрация ###
# ? Добавление нового пользователя в БД, выдача ему токенов. 

# То есть, если нажимают, летит запрос и почта подтвержается

app.route('/email_code', methods=['GET', 'POST']) # Отправка кода на указанный email
def email_code(): #! Сделать авторизацию через email - страницу. Получение КОДА !!!! Нужно вводить код
    return jsonify(200)


@app.route('/email_code_repeat', methods=['GET', 'POST'])
def email_code_repeat(): # Повторная отправка email, если оно не пришло или было отправлено некорректно
    return jsonify(200)



@app.route('/email_confirm', methods=['GET', 'POST'])
def email_confirm():
    return jsonify(200) #! Подтверждение той электронной почты, на которую было отправлено писмьо. После того, как нажали


@app.route('/registration', methods=['POST'])
async def registration(): # Ввод личных данных при регистрации в приложении и запись данных в БД 
    if request.method == 'POST':

        info = await request.get_json()
        if not all(k in info for k in ('username', 'email', 'password', 'city')):
            return jsonify({'code': 400, 'message': 'Не хватает аргументов'})
        
        if await database.registration(info['username'], info['email'], info['password'], info['city'], info['billings'], info['wishlist']):
            result = await create_couple_by_email(info['email'])

            return jsonify({
                    'code': 200,
                    'message': 'Пользователь с email: {} успешно зарегистрирован'.format(info['email']),
                    'access_token': result['access_token'],
                    'refresh_token': result['refresh_token']
                })
        else:
            abort(400)
    
    
### Конец регистрации ###


### Сервисные специальные методы ###
# ? Нужны для принудительного игнорирования общего алгоритма

# ! Сервисный метод. Не использовать в общем алгоритме. Вызывается при возникновении ошибок, либо при принудительном игнорировании алгоритма
app.route('/create_refresh_by_email', methods=['GET', 'POST']) #? Отдельный метод для создания рефреш-токена
async def create_refresh_by_email(): # GET 
    #TODO Передавать параметром email для создания нового рефреша
    return jsonify(200)

# ! Сервисный метод. Не использовать в общем алгоритме. Вызывается при возникновении ошибок, либо при принудительном игнорировании алгоритма
app.route('/create_access_by_email', methods=['GET', 'POST']) #? Отдельный метод для создания аксесс-токена
async def create_access_by_email(): # GET 
    #TODO Передавать параметром email для создания нового аксесса
    return jsonify(200)

app.route('/create_access_by_refresh', methods=['GET', 'POST']) #? Ручка обновления аксесс-токена
def create_access_by_refresh(): # GET 
    #TODO Передавать в контексте рефреш, по которому нужно будет все обновить
    return jsonify(200)


### Конец сервисных методов ###


### Личный профиль пользователя. Пользовательский сценарий (авторизация) ###
#? Все, что связано с профилем пользователя, выдача информации / редактирование информации

### Конец методов работы с профилем пользователя ###

### Дополнительные методы ###
#? Рекомендации по уходу, о нас, магазины и тд. Все, что может быть дополнительным


### Конец дополнительных методов ###


### Методы работы с магазином ###
#? Все, что касается магазина, товаров, заказов



if __name__ == '__main__':
    app.run(host="localhost", debug=True, port=8080, threaded=True)