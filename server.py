from quart import Quart
from quart import jsonify
from quart import request, abort
from service import TokenProcess
from config import INSALES_URL
from database import Database
import requests
from tools import html_parser
import asyncio
import requests
import json
from email_processing import EmailProcessing
from sessions_processing import SessionProcessing


class DatabaseProcess:
    def __init__(self):
        return
    
    async def get_product_list(self, collection_id):
        # Получение полного списка продуктов по данной категории
        return requests.get(INSALES_URL + '/' + 'collects.json', params={'collection_id': str(collection_id)}).json() #?
    
    async def product_listing(self, collection_id): # ollection_id=20742662
        # Получение информации по данному продукту в очереди
        info = await self.get_product_list(collection_id)
        for i in info:
            try:
                product_information = requests.get(INSALES_URL + '/' + 'products/{}.json'.format(i['product_id'])).json()
                result = await self.product_updating(product_information)
                if result: pass # ? else... 
            except Exception as e:
                print(e)
                continue
        return True

    async def product_updating(self, product_information):

        material = '' 
        colour = ''
        brand = ''
        size = ''
        image = ''

        images = product_information['images']
        for im in images:
            image = im['original_url']
            break
        
        for t in product_information['characteristics']:
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

                
                #lol = json.dumps(info['collections_ids'])
                #print(type(lol))
        
        
        product_card = {
                'available': str(product_information['available']),
                'category_id': product_information['category_id'],
                'collections_ids': json.dumps(product_information['collections_ids']),
                'material': material, 'colour': colour,
                'brand': brand, 'size': size,
                'price': int(float(product_information['variants'][0]['base_price'])), 
                'description': html_parser(product_information['description']),
                'insales_id': product_information['id'], 'title': product_information['title'],
                'variants': [ii['id'] for ii in product_information['variants']],
                'images': image
                        }
        result = await Database().update_products(product_card)

    def between_callback(self, collection_id):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.product_listing(collection_id))
        loop.close()



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
def index():
    '''
    Тестирование сервера (связи с сервером).
    Получение конфигурации сервера
    '''
    return jsonify({
        'code': 200, 'message': 'Конфигурация нормальная. Сервер ждет команд'})


@app.route('/shop_collections', methods=['GET'])
async def shop_collections():
    '''
    Получение коллекций напрямую из магазина
    '''
    info = requests.get(INSALES_URL + '/' + 'collections.json').json()
    return jsonify({'code': 200, 'catalog': info})


@app.route('/token_couple', methods=['POST'])
async def token_couple():
    '''
    Получение пары токенов для email
    # TODO: сделать метод проверки достоверности access для защиты данного метода
    #? Если токен действителен, то отправлять сразу пару
    '''
    info = await request.get_json()
    result = await token_process.create_couple(info.get('email'))
    return jsonify({
        'code': 200,
        'access_token': result['access_token'],
        'refresh_token': result['refresh_token']})


@app.route('/get_info', methods=['POST'])
async def get_info():
    """
    Получить информацию по токену можно только в том случае,
    если пользователь авторизован. Его access_token будет дейсителен.
    Таким образом проверяется только access_token. 
    """
    info = await request.get_json()
    access_token = info.get('access_token')


@app.route('/update_collections_db', methods=['GET'])
async def update_collections_db():
    '''
    Обновление всех коллекций в БД
    # TODO: Почистить описание коллекций от различного рода "HTML - мусора"
    '''
    info = requests.get(INSALES_URL + '/' + 'collections.json').json()
    for i in info:
        result = await database.add_collections(i['id'], i['parent_id'], i['title'], str(i['description']))
        if result: pass # Выполнение функции
        else: abort(405) #? Не получилось добавить ту или иную коллекцию
        
    return jsonify({'code': 200, 'message': 'Все коллекции успешно добавлены'})

         
@app.route('/shop_products', methods=['GET'])
def get_products():
    '''
    Получение всех продуктов из БД
    '''
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


@app.route('/db_collections', methods=['GET'])
async def db_collections():
    """
    Получение коллекций из БД
    """
    result = await database.get_all_collections()
    return jsonify({'code': 200, 'message': result})


@app.route('/db_products', methods=['GET'])
async def db_products():
    """
    Получение всех продуктов из БД
    """
    result = await database.get_product_list()
    return jsonify({'code': 200, 'message': result})


@app.route('/product_byid', methods=['GET'])
async def product_byid():
    """
    Получение информации о продукте из БД по его ID (Insales ID)
    """
    info = await request.get_json()
    insales_id = info['insales_id']
    product_information = await database.get_product_from_db_byid(insales_id)
    #info_id, info_title = await database.get_category_title_and_id_by_product_id(product_information['insales_id'])
        
    return jsonify({
        'code':200, 'product_info': product_information})
        #'category': info_title, 'category_id': info_id})


@app.route('/collection_byid', methods=['GET'])
async def collection_byid():
    """
    Получение полностью информации о категории по ID
    """
    info = await request.get_json()
    collection_id = info['collection_id']
    result  = await database.get_collection_by_id(collection_id)

    return jsonify({
        'code': 200, 'category': result})

'''
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
'''

@app.route('/update_db', methods=['GET'])
# Обноелние / запись пролуктов в БД
async def update_db():
    info = requests.get(INSALES_URL + '/' + 'collections.json').json()
    for i in info:
        result = await database.add_collections(i['id'], i['parent_id'], i['title'], str(i['description']))
        if result: continue
        else: return jsonify({'code': 400,'message':'Ошибка в добавлении категории в БД'})
    print('Все коллекции в БД обновлены. Старт заполнения товаров')
    
    collections = await database.get_collections_id_from_db()    
    collections = [coll['insales_id'] for coll in collections]

    '''
    for coll in collections:
        print(coll)
        t = threading.Thread(target=DatabaseProcess().between_callback, args=(coll,))
        t.start()
        print('Поток для {} категории запущен'.format(coll))

    return jsonify({'code': 200,
        'message': 'Проверка'})
    '''

    for coll in collections:
        result = await DatabaseProcess().product_listing(coll)
        if result: pass
        print('Добавлено')
    
    return jsonify({'code': 200,
        'message': 'Проверка'})


@app.route('/get_all_shop_collections', methods=['GET'])
async def get_all_shop_collections():
    """
    Получение всех коллекций из магазина напрямую
    """
    return requests.get(INSALES_URL + '/' + 'collections.json').json()


@app.route('/get_db_products_by_collection', methods=['GET'])
async def get_db_products_by_collection():
    """
    Получение всех товаров из БД по одной коллекции
    """
    info = await request.get_json()
    collection_id = info['collection_id']
    result = await database.check_collections_from_product(collection_id)
    return jsonify({
        'code':200,
        'message': 'Все товары получены успешно',
        'catalog': result})


@app.route('/send_email', methods=['GET'])
async def email_confirm():
    '''
    Подтверждение электронной почты. Если код, отправленный и введенный совпадают, то пользователь может выполнить регистрацию.
    Для повторного запроса вызывается тот же самый метод. 
    '''
    info = await request.get_json()
    email_aim = info['email']

    result = await EmailProcessing().send_email(email_aim)
    return jsonify({
        'code': 200,
        'message': 'Код успешно отправлен {}'.format(email_aim),
        'verification_code': result 
    })


@app.route('/registration', methods=['POST'])
async def registration(): 
    """
    Регистрация производися уже непосредственно после того, как почта пользователя была подтверждена.
    Вначале переменные хранятся локально, чтобы затем их передать в данный запрос.
    """
    if request.method == 'POST':

        info = await request.get_json()
        if not all(k in info for k in ('name', 'email', 'password', 'city')):
            return jsonify({'code': 400, 'message': 'Не хватает аргументов'})
        
            
        result = await database.registration(info['name'], info['email'], info['password'], info['city'], info['orders'], info['wishlist'])
        if result: pass
        couple = await token_process.create_couple(info['email'])
            
            
            # Регистрация нового пользователя в InSales
        '''
            if result:
                return requests.post(INSALES_URL + '/' + 'clients.json',json={
            'client': {
                'name': info['name'],
                'surname': info['surname'],
                'middlename': info['middlename'],
                'registered': True,
                'email': info['email'],
                'password': info['password'],
                'phone': info['phone'],
                'type': 'Client::Individual'
                }}).json()
        '''
            
        try:
            _session = await SessionProcessing().create_session(info['email'])
        except Exception as e:
            print(e, 'Возникла ошибка при создании новой сессии')
            pass

        return jsonify({
                'code': 200,
                'message': 'Пользователь с email: {} успешно зарегистрирован'.format(info['email']),
                'access_token': couple['access_token'],
                'refresh_token': couple['refresh_token']})
    else:
        abort(400)


@app.route('/login', methods=['POST'])
async def login():

    if request.method == 'POST':
        info = await request.get_json()
        email = info['email']
        password = info['password']

        result = await database.login(email, password)
        if result: pass
        couple = await token_process.create_couple(email)

        try:
            _session = await SessionProcessing().create_session(info['email'])
        except Exception as e:
            print(e, 'Возникла ошибка при создании новой сессии')
            pass

        return jsonify({
                'code': 200,
                'message': 'Авторизация успешна. Для пользователя была сформирована новая пара токенов для обслуживания',
                'access_token': couple['access_token'],
                'refresh_token': couple['refresh_token']
            })
        
    else:
        abort(400)


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