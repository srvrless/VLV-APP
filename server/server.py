from quart import Quart
from quart import jsonify
from quart import request
from quart import render_template
from server_helpers.token_factory import create_couple_by_email
from database import Database
from quart import abort
from server_helpers.tools import html_parser
import json
import requests



app = Quart(__name__)

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


@app.route('/get_prod_shop', methods=['GET'])
async def get_prod_shop():

    if request.method == 'GET':
        prod_box = []
        for page in range(1, 201):
            prod_box.append(requests.get(insales_url + '/' + 'products.json', params={'page_sise': 100, 'page': page}).json())

        return jsonify({
            'coee': 200,
            'info': prod_box
        })

    
@app.route('/update_prod_db', methods=['GET'])
async def update_products_in_database():
    if request.method == 'GET':

        box_variants = []
        
        for page in range(1, 201):
            images = []
            material = '' 
            colour = ''
            brand = ''
            size = ''
            price = ''
            info = requests.get(insales_url + '/' + 'products.json', params={'page_sise': 100, 'page': page}).json()
            
            for i in info:
                try:
                    for q in i['images']:
                        images.append(q['compact_url'])
                        images.append(q['large_url'])
                        images.append(q['medium_url'])
                        images.append(q['original_url'])
                        images.append(q['small_url'])
                        images.append(q['thumb_url'])
                        images.append(q['url'])

                except Exception as e:
                    print('Ошибка при добавлении изображений: {}'.format(e))
                    pass


                for t in i['characteristics']:
                    if t['property_id'] == 40865551: # Материал
                        material = t['title']
                    elif t['property_id'] == 37399009: # Цвет
                        colour = t['title']
                    elif t['property_id'] == 35926723: # Бренд
                        brand = t['title']
                    elif t['property_id'] == 35932191: #? Размер
                        size = t['title']
                    #elif t['property_id'] == 35934755:
                       # price = t['title']
                
                if len(size) != 0 or size != '' or size is not None:
                    if type(size) != list:
                        size = size.split(',')
                        size = [s.replace(' ', '') for s in size]
                        try: size = [float(s) for s in size]
                        except: pass
                
            
                product = {
                        'available': str(i['available']),
                        'category_id': i['category_id'],
                        'material': material,
                        #'ads_category': i['characteristics'][1]['title'],
                        'colour': colour,
                        'brand': brand,
                        'size': size,
                        'price': int(float(i['variants'][0]['base_price'])), 
                        'description': html_parser(i['description']),
                        'insales_id': i['id'],
                        'title': i['title'],
                        'variants': [ii['id'] for ii in i['variants']],
                        'images': json.dumps(images)
                        }

                images = []
                result = await database.update_products(product)
        
        return jsonify({
            'code': 200,
            'message': 'All products were successfully updated in the database.'
            })

    return jsonify({'code': 405,
        'message': 'The method specified in the request is not allowed for the resource identified by the request URI.'
        })


@app.route('/product_card', methods=['GET', 'POST']) #? Карточка товара по информации из БД
# ? NoAuth
async def get_product_id():
    if request.method == 'GET':
        title = request.args.to_dict()['title']

        product_information = await database.get_product_by_title(title)
        info_id, info_title = await database.get_category_title_and_id_by_product_id(product_information['insales_id'])
        

        return jsonify(
            {
                'code':200,
                'product_info': product_information,
                'category': info_title,
                'category_id': info_id
            })

    return jsonify(
        {
        'code': 202,
        'message': 'Данный метод не поддерживается'
        })


@app.route('/get_prod_from_coll_title', methods=['GET', 'POST']) #? Получение полного списка продуктов по названию конкретной категории
async def get_products_from_category_title():
    if request.method == 'GET':
        category = request.args.to_dict()['category']

        try:
            result = await database.get_all_products_from_category_title(category)
            
        except Exception as e:
            return jsonify({
                    'code': 403,
                    'message': 'Возможно, нет категории под таким названием'
                })
        
        return jsonify({
            'code': 200,
            'catalog': result
            })

    return jsonify({
        'code': 202,
        'message': 'Данный метод не поддерживается'
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
@app.route('/create_access_by_email', methods=['GET', 'POST']) #? Отдельный метод для создания аксесс-токена
async def create_access_by_email(): # GET 
    #TODO Передавать параметром email для создания нового аксесса
    return jsonify(200)

@app.route('/create_access_by_refresh', methods=['GET', 'POST']) #? Ручка обновления аксесс-токена
def create_access_by_refresh(): # GET 
    #TODO Передавать в контексте рефреш, по которому нужно будет все обновить
    return jsonify(200)


@app.route('/create_couple_by_email', methods=['GET', 'POST']) #? Обноление пары токенов
async def update_couple(): # GET 

    info = await request.get_json()
    email = info['email']

    result = await create_couple_by_email(email)

    return jsonify({
            'code': 200,
            'acess_token': result['access_token'],
            'refresh_token': result['refresh_token']
        })


### Конец сервисных методов ###


### Личный профиль пользователя. Пользовательский сценарий (авторизация) ###
#? Все, что связано с профилем пользователя, выдача информации / редактирование информации

### Конец методов работы с профилем пользователя ###


if __name__ == '__main__':
    app.run(host="localhost", debug=True, port=8080, threaded=True)