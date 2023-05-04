from quart import Quart
from quart import jsonify
from quart import request, abort
from service import TokenProcess
from config import INSALES_URL
from database import Database
import requests
import json
from tools import html_parser


#TODO Для создания повышенного уровня защиты, необходимо внедрить проверку на пользователя: Есть ли этот пользователь в БД или нет.
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


app = Quart(__name__)
database = Database()
token_process = TokenProcess()


@app.route('/', methods=['GET'])
# Тест сервера
def index():
    return jsonify({
        'code': 200, 'message': 'Тест сервера'})


@app.route('/shop_collections', methods=['GET'])
# Получение коллекций напрямую из магазина
async def shop_collections():
    info = requests.get(INSALES_URL + '/' + 'collections.json').json()
    return jsonify({'code': 200, 'catalog': info})


@app.route('/token_couple', methods=['POST'])
# Создание пары токенов по конкретному email
async def token_couple():
    info = await request.get_json()
    result = await token_process.create_couple(info.get('email'))
    return jsonify({
        'code': 200,
        'access_token': result['access_token'],
        'refresh_token': result['refresh_token']})


@app.route('/update_collections_db', methods=['GET'])
async def update_collections_db():
    info = requests.get(INSALES_URL + '/' + 'collections.json').json()
    for i in info:
        result = await database.add_collections(i['id'], i['parent_id'], i['title'], str(i['description']))
        if result: pass # Выполнение функции
        else: abort(405) #? Не получилось добавить ту или иную коллекцию
        
    return jsonify({'code': 200, 'message': 'Все коллекции успешно добавлены'})

         
@app.route('/get_products', methods=['GET'])
# Обноелние / запись пролуктов в БД
def get_products():
    catalog = []
    page = 0
    try:
        while True:
            page += 1
            catalog.append(requests.get(INSALES_URL + '/' + 'products.json', params={'page_sise': 100, 'page': page}).json())

    except Exception as e:
        return jsonify({
            'code': 201,
            'message': 'Функция отработала по прерыванию количества страниц. Каталог товаров передан. Ответ: {}'.format(e),
            'catalog': catalog})

    finally:
        return jsonify({'coee': 200, 'catalog': catalog})


@app.route('/update_db', methods=['GET'])
# Обноелние / запись пролуктов в БД
async def update_db():
    info = requests.get(INSALES_URL + '/' + 'collections.json').json()
    for i in info:
        result = await database.add_collections(i['id'], i['parent_id'], i['title'], str(i['description']))

        if result:
            products = requests.get(INSALES_URL + '/' + 'collects.json', params={'collection_id': i['id']}).json()

            for product in products:

                info = requests.get(INSALES_URL + '/' + 'products/{}.json'.format(product['product_id'])).json() #!!!!
                material = '' 
                colour = ''
                brand = ''
                size = ''

                images = info['images']
                for im in images:
                    image = im['original_url']
                    break
        
                for t in info['characteristics']:
                    # Материал
                    if t['property_id'] == 40865551: material = t['title']
                    # Цвет
                    elif t['property_id'] == 37399009: colour = t['title']
                    # Бренд
                    elif t['property_id'] == 35926723: brand = t['title']
                    #? Размер
                    elif t['property_id'] == 35932191: size = t['title']
                        #elif t['property_id'] == 35934755: price = t['title']
                
                if len(size) != 0 or size != '' or size is not None:
                    if type(size) != list:
                        size = size.split(',')
                        size = [s.replace(' ', '') for s in size]
                        try: size = [float(s) for s in size]
                        except: pass
                
                product_info = {
                        'available': str(info['available']),
                        'category_id': info['category_id'],
                        'collection_ids': info['collection_ids'],
                        'material': material, 'colour': colour,
                        'brand': brand, 'size': size,
                        'price': int(float(info['variants'][0]['base_price'])), 
                        'description': html_parser(info['description']),
                        'insales_id': info['id'], 'title': info['title'],
                        'variants': [ii['id'] for ii in info['variants']],
                        'images': image
                        }

                result = await database.update_products(product_info)
        
        return jsonify({
            'code': 200,
            'message': 'Все продукты и категории были успешно обновлены в БД.'})

    return jsonify({'code': 405,
        'message': 'The method specified in the request is not allowed for the resource identified by the request URI.'})



@app.route('/db_collections', methods=['GET'])
async def db_collections():
    """
    Получение коллекций из БД
    """
    result = await database.get_all_collections()
    return jsonify({'code': 200, 'message': result})


@app.route('/db_products', methods=['GET'])
# Получение продуктов из БД
async def db_products():
    result = await database.get_product_list()
    return jsonify({'code': 200, 'message': result})


@app.route('/product_byid', methods=['GET'])
# Получение информации о конкретном товаре по ID - товара
async def product_byid():
    title = request.args.to_dict()['title']
    product_information = await database.get_product_by_title(title)
    info_id, info_title = await database.get_category_title_and_id_by_product_id(product_information['insales_id'])
        
    return jsonify({
        'code':200, 'product_info': product_information,
        'category': info_title, 'category_id': info_id})


@app.route('/collection_byid', methods=['GET'])
# Получение товаров из коллекции по ID
def collection_byid():
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })


@app.route('/collection_bytitle', methods=['GET'])
# Получение товаров из коллекции по названию
async def collection_bytitle():
    info = await request.get_json()
    category = info['category']

    try:
        result = await database.get_all_products_from_category_title(category)
    except Exception as e: return jsonify({
                    'code': 403,
                    'message': 'Возможно, нет категории под таким названием. Ошибка: {}'.format(e)})
        
    return jsonify({'code': 200,'catalog': result})


@app.route('/get_shop_products_by_collection', methods=['GET'])
async def get_products_by_collection():
    """
    Получение продуктов по категории напрямую с магазина
    """
    info = await request.get_json()
    collection_id = info['collection_id']
    return requests.get(INSALES_URL + '/' + 'collects.json', params={'collection_id': collection_id}).json()


@app.route('/get_shop_collections_by_product', methods=['GET'])
async def get_collections_by_product():
    """
    Получение коллекций по указанию ID продукта напрямую из магазина
    """
    info = await request.get_json()
    product_id = info['product_id']
    return requests.get(INSALES_URL + '/' + 'collects.json', params={'product_id': product_id}).json()


@app.route('/get_shop_collection', methods=['GET'])
async def get_shop_collection():
    """
    Получение полной информации о коллекции напрямую из магазина
    """
    info = await request.get_json()
    collection_id = info['collection_id']
    return requests.get(INSALES_URL + '/' + 'collections/{}.json'.format(collection_id)).json()


@app.route('/get_all_shop_collections', methods=['GET'])
async def get_all_shop_collections():
    """
    Получение всех коллекций из магазина напрямую
    """
    return requests.get(INSALES_URL + '/' + 'collections.json').json()


@app.route('/get_db_products_by_collection', methods=['GET'])
def get_db_products_by_collection():
    return 


@app.route('/registration', methods=['POST'])
# Регистрация нового пользователя
async def registration(): 
    if request.method == 'POST':

        info = await request.get_json()
        if not all(k in info for k in ('username', 'email', 'password', 'city')):
            return jsonify({'code': 400, 'message': 'Не хватает аргументов'})
        
        if await database.registration(info['username'], info['email'], info['password'], info['city'], info['billings'], info['wishlist']):
            result = await token_process.create_couple(info['email'])

            return jsonify({
                    'code': 200,
                    'message': 'Пользователь с email: {} успешно зарегистрирован'.format(info['email']),
                    'access_token': result['access_token'],
                    'refresh_token': result['refresh_token']
                })
        else:
            abort(400)


@app.route('/email_confirm', methods=['GET', 'POST'])
def email_confirm():
    return jsonify(200)


@app.route('/email_code_repeat', methods=['GET', 'POST'])
def email_code_repeat(): # Повторная отправка email, если оно не пришло или было отправлено некорректно
    return jsonify(200)


app.route('/email_code', methods=['GET', 'POST'])
def email_code(): 
    return jsonify(200)


@app.route('/login', methods=['POST'])
async def login():

    if request.method == 'POST':
        info = await request.get_json()
        email = info['email']
        password = info['password']

        if await database.login(email, password):

            result = await token_process.create_couple(email)

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


@app.route('/get_info', methods=['POST'])
async def get_info():
    """
    Получить информацию по токену можно только в том случае,
    если пользователь авторизован. Его access_token будет дейсителен.
    Таким образом проверяется только access_token. 
    """
    info = await request.get_json()
    access_token = info.get('access_token')


@app.route('/offer', methods=['POST'])
# Оформление заказа черех мобильное приложение
def offer():
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })


@app.route('/add_towishlist', methods=['POST'])
# Добавление товара в вишлист
def add_towishlist():
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })


@app.route('/add_tocart', methods=['POST'])
# Добавление товара в вишлист
def add_tocart():
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })


@app.route('/delete_fromwishlist', methods=['POST'])
# Удаление товара из вишлиста
def delete_fromwishlist():
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })


@app.route('/delete_fromcart', methods=['POST'])
# Удаление товара из корзины
def delete_fromcart():
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })


@app.route('/get_fromwishlist', methods=['POST'])
# Получение товара из вишлиста
def get_fromwishlist():
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })


@app.route('/get_fromcart', methods=['POST'])
# Получение товара из вишлиста
def get_fromcart():
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })



if __name__ == '__main__':
    app.run(host="localhost", debug=True, port=8080, threaded=True)