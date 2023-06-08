


'''
### Admin Pannel ###
@app.route('/admin', methods=['GET', 'POST']) # Страница перехода на админпанель
async def admin():
    if request.method == 'POST': # ? Вход в Административную панель по логину и паролю администратора
        return jsonify( #! Дописать
            {
                'code': 200,
                'message': 'Admin'
            } #! Если все хорошо, то переход на главную страницу администратора
        )
    
    if request.method == 'GET': #? Переход (просто вывод страницы администратора)
        return await render_template('admin_enter.html')




#! необходимо на эту страницу сначала выводить имебщиеся баннеры, чтобы их можно было редактировать
@app.route('/banner_edit', methods=['GET', 'POST']) # Функция взаимодействия (редактирования / добавления баннеров)
async def banner_edit():
    
    if request.method == 'GET': #! Доделать
        return render_template('banners.html') # ? переход на страницу добавления / редактирования баннеров
    
    if request.method == 'POST': #! Доделать
        return jsonify(200) # ? Добавление нового баннера (загрузка с компьютера). Заполнение полей бренда и названия





@app.route('/get_banners', methods=['GET', 'POST']) # Получение баннеров (вывод)
def get_banners():
    return jsonify('DB information') #! 
'''



'''
#? Потом будет доработано. В следующих итеррациях
@app.route('/password_recovery', methods=['GET', 'POST'])
async def password_recovery():

    if request.method == 'POST':

        access_token = request.headers.get('acess_token')

        response = await server_controller.validate_access_token(access_token)

        if response['code'] == 200:
            email = server_controller.email_from_token(access_token)

            if await server_controller.code_collector(email):
                return jsonify(
                    {
                    'code': 200,
                    'message': 'Код проверки отправлен на электронную почту'
                    }
                )
            
            else:
                return jsonify(
                    {
                    'code': 401,
                    'message': 'Сообщение на почту не было отправлено'
                    }
                )
        
        else:
            return jsonify(
                {
                'code': 400,
                'message': 'Возможно, ошибка в проверке токена'
                }
            )
    
    return jsonify(
        {
        'code': 202,
        'message': 'Данный метод не поддерживается'
        })


@app.route('/accept_recovery', methods=['GET', 'POST'])
async def accept_recovery():

    if request.method == 'POST':

        access_token = request.headers.get('acess_token')

        response = await access_token(access_token)

        if response['code'] == 200:
            email = server_controller.email_from_token(access_token)

            if await server_controller.decrypt_code_collector(email):
                return jsonify(
                    {
                    'code': 200,
                    'message': 'Успешное подтверждение'
                    }
                )
            
            else:
                return jsonify(
                    {
                    'code': 401,
                    'message': 'Код, отправленный на почту не подтвержден. Возможно иная ошибка в процессе дешифрования'
                    }
                )
        
        else:
            return jsonify(
                {
                'code': 400,
                'message': 'Возможно, ошибка в проверке токена'
                }
            )
    
    return jsonify(
        {
        'code': 202,
        'message': 'Данный метод не поддерживается'
        })
'''


'''
#? В текущей версии данный метод выполняется на Front-end 

@app.route('/check_logged_in', methods=['GET', 'POST'])
async def check_logged_in():

    if request.method == 'GET':
        return jsonify(
            {
                'code': 200,
                'message': 'Для использования данного метода запрос должен быть POST. Метод возвращает флаг авторизации пользователя в системе'
            }
        )
    
    elif request.method == 'POST':

        access_token = request.headers.get('access_token')
        refresh_token = request.headers.get('refresh_token')

        result = await process(access_token, refresh_token)

        if result:

            email = await decrypt_and_get_email(refresh_token)
            status = await ssession.check_logged(email)

            if status:
                return jsonify(
                    {
                        'code': 200,
                        'message': 'Пользователь авторизован'
                    }
                )
            
            else:
                return jsonify(
                    {
                        'code': 202,
                        'message': 'Пользователь не авторизован'
                    }
                )

        else: 
            return jsonify(
                {
                    'code': 400,
                    'message': 'Доступ заблокирован. Необходимо выяснить причину и исправить это'
                }
            )

'''



'''
@app.route('/personal_information', methods=['GET', 'POST']) #? модуль смены / обновления пользовательской персональной информации (основной)
async def personal_information():

    if request.method == 'GET':

        info = await request.get_json() # Достается персональная информация по email, который присылается параметром

        return jsonify(
            {
                'code': 200,
                'catalog': 'Information' #! Добавить вывод из БД личной информации пользователя
            }
        )
    
    elif request.method == 'POST':

        access_token = request.headers.get('access_token')
        refresh_token = request.headers.get('refresh_token')

        result = await token_process(access_token, refresh_token)

        if result:

            name = request.headers.get('name')
            secod_name = request.headers.get('second_name')
            phone = request.headers.get('phone')

            email = await decrypt_and_get_email(refresh_token)

            
            # Здесь код добавления всей этой информации в БД пользователя,
            # то есть обновление его информации
            
        
        else:
            return jsonify(
                {
                    'code': 403,
                    'message': 'Не был предоставлен доступ'
                }
            )
        
        return jsonify(
            {
                'code': 200,
                'message': 'Информация пользователя успешно обновлена'
            }
        )
'''


'''
@app.route('/extra_personal_information', methods=['GET', 'POST']) #? модуль добавления информации об адресе и о доставке
async def extra_personal_information():
    #! Адрес доставки. Для добавления адреса доставки нужно обработать весь список городов, выдать самые релевантные варианты
    return
'''


'''
@app.route('/add_to_cart', methods=['GET', 'POST']) #? Добавление товара в корзину
async def add_to_cart():
    if request.method == 'POST':
        info = await request.get_json()

        access_token = request.headers.get('acess_token')
        refresh_token = request.headers.get('refresh_token')

        result = await token_process(access_token, refresh_token)
        response_from_validate = await token_validate_process(result)

        if response_from_validate['code'] == 200:
            pass
        else:
            return response_from_validate['message']
        
        email = await decrypt_and_get_email(access_token)
        
        if ssession.insert_into_cart(email, info['product_id']):
            return jsonify({
                    'code': 200,
                    'message': 'Товар успешно добавлен в корзину'
                })

    else: 
        return jsonify({
        'code': 400,
        'message': 'Данный метод не поддерживается.'
        })
'''





'''
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


@file_decorator.write_file_decorator
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
    
    async def check_logged(self, email):
        data = get_data_fromfile()

        if data['catalog'][email]['logged_in']:
            return True
        else: return False

    
'''




"""
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
                'collections_ids': product_information['collections_ids'],
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

"""