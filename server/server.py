from quart import Quart, jsonify, request, abort
import requests

from service import TokenProcess
from config import INSALES_URL
from db.database import Database
from email_processing import EmailProcessing
from sessions_processing import SessionProcessing
from db.database_updater import DatabaseUpdater
from insales_api import InsalesApi

from tools import json_args, query_args, token_required, Translitor
import http_code

#TODO Для создания повышенного уровня защиты, необходимо внедрить проверку на пользователя: Есть ли этот пользователь в БД или нет.
#TODO Добавлеие новых баннеров в БД
#TODO Вывод товаров из БД, чтобы их отображать на странице
#TODO Проверка, чтобы администратор был авторизован: Защита от перехода поперек пользовательского сценария
#TODO Добавление нового баннера / редактирование тех баннеров, которые есть сейчас на странице
#TODO: Вставить в программный код места, где создаются новые сессии и они управляются
#TODO: Сделать автоматическую выдачу токена при проверке рефреш, если рефреш еще действует (сейчас в ручном)
#TODO: В базу данных каждоо пользователя добавить поле "История заказов".
    ##? Добавить отдельный параметр вывода заказов, которые были когда-либо связаны с профилем (отдельный счетчик)
    ##? Вставить в программный код все, что касается истории заказов пользователя

#TODO: Каждому пользователю добавить поле, в котором будет содердаться информация о текущих его заказах.
    # Это должна быть отдельная таблица, в которой все это будет обрабатываться. Чтобы всю 
    # информацию можно было бы оттуда брать. И выдвать на экране

#TODO: сделать метод смены электронной почты с подтверждением через письмо также, как и было при регистрации
#TODO: сделать метод подтверждения номера телефона через смс, как и положено ----> подключиь для этого сторонний смс сервис
#TODO: Сделать метод удаления профиля
#TODO: написать функцию смены пароля и подтверждение данного действия через смс.
#TODO: Сделать таблицу отдельную, в которой будет список магазинов
#TODO Нужно нажать на кнопку на почте, чтобы ее подтвердить. 
#TODO Записать в БД статус электронной почты (код)
#TODO Отправка уведомдения о том, что код был неверный (если его ввели неверно)

#TODO Добавить в получении товаров возможность отдачи товаров постепенно. Добавить такую возможность для всего, выделить для абстракт


app = Quart(__name__)
database = Database()
database_updater = DatabaseUpdater(database)
token_process = TokenProcess()
insales_api = InsalesApi()
translitor = Translitor(database)
# translitor.init()


@app.route('/', methods=['GET'])
def index():
    """ Тестирование сервера (связи с сервером). Получение конфигурации сервера """
    return jsonify({
        'code': 200, 'message': 'Конфигурация нормальная. Сервер ждет команд'})

# ==== clients ====

@app.route('/get_client_info', methods=['GET'])
@token_required
async def get_client_info(email):
    """ 
    Получить информацию по токену можно только в том случае,
    если пользователь авторизован. Его access_token будет действителен.
    Таким образом проверяется только access_token. 
    """
    try:
        result = await database.get_client_by_email(email)
        
        return jsonify({
            "client": result
        }), http_code.ok
    except Exception as e:
        return jsonify({
            "message": "Ошибка при обработке",
            "error": str(e)
        }), http_code.internal_server_error


# ==== authorization ====

# @app.route('/token_couple', methods=['POST'])
# async def token_couple():
#     """
#     Получение пары токенов для email
#     # TODO: сделать метод проверки достоверности access для защиты данного метода
#     #? Если токен действителен, то отправлять сразу пару
#     """
#     info = await request.get_json()
#     result = await token_process.create_couple(info.get('email'))
#     return jsonify({
#         'code': 200,
#         'access_token': result['access_token'],
#         'refresh_token': result['refresh_token']
#     })


@app.route('/send_email', methods=['GET'])
@query_args(required="email")
async def email_confirm():
    """ 
    Подтверждение электронной почты. Если код, отправленный и введенный совпадают, то пользователь может выполнить регистрацию.
    Для повторного запроса вызывается тот же самый метод. 
    """
    email_aim = request.args.get("email", type=str)

    result = await EmailProcessing().send_email(email_aim)
    return jsonify({
        "message": "Код успешно отправлен на почту {}".format(email_aim),
        "verification_code": result 
    }), http_code.ok


@app.route('/guest_login', methods=['GET', 'POST'])
@query_args(required="email")
async def guest_login():
    """ 
    Гостевой вход. Требуется только email. В базе сохраняется как гостевой аккаунт, 
    в перспективе с него же можно будет зайти даже на другом устройстве.
    В insales ничего не сохраняется 
    """
    email = request.args.get("email", type=str)
    result = await database.guest_login(email)

    if result["is_guest"]:
        couple = await token_process.create_couple(email)

        result["access_token"] = couple["access_token"]
        result["refresh_token"] = couple["refresh_token"]
        return jsonify(result), http_code.ok
    else:
        result["access_token"] = None
        result["refresh_token"] = None
        return jsonify(result), http_code.forbidden


# TODO добавить регистрацию в insales
@app.route('/registration', methods=['POST'])
@json_args(required=("name", "surname", "phone", "email", "password"), possible=("birth_date", "middlename"))
async def registration(): 
    """
    Регистрация производится уже непосредственно после того, как почта пользователя была подтверждена.
    Вначале переменные хранятся локально, чтобы затем их передать в данный запрос.
    """
    info = await request.get_json()

    name, surname, phone, email, password = info["name"], info["surname"], info["phone"], info["email"], info["password"]
    birth_date = info["birth_date"] if "birth_date" in info else None
    result = await database.registration(name, surname, phone, email, birth_date, password)
    if not result:
        return jsonify({
            'message': f"Пользователь с email {info['email']} уже зарегистрирован"
        }), http_code.forbidden

    couple = await token_process.create_couple(info['email'])
        
        # Регистрация нового пользователя в InSales
    
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
    
        
    try:
        _session = await SessionProcessing().create_session(info['email'])
    except Exception as e:
        print(e, 'Возникла ошибка при создании новой сессии')
        pass

    return jsonify({
        "message": "Пользователь с email {} успешно зарегистрирован".format(info["email"]),
        "access_token": couple["access_token"],
        "refresh_token": couple["refresh_token"]
    }), http_code.ok


# TODO добавить обновление последних пользователей, вдруг человек логинится, а регистрация была на сайте 5 минут назад
@app.route('/login', methods=['POST'])
@json_args(required=("email", "password"))
async def login():
    """ Метод, осуществляющий логин пользователя. Логин идет через insales """
    info = await request.get_json()
    email = info["email"]
    password = info["password"]

    result = await insales_api.login(email, password)
    if not result:
        return jsonify({
            "message": "Неправильные логин или пароль",
        }), http_code.forbidden
    
    couple = await token_process.create_couple(email)

    try:
        _session = await SessionProcessing().create_session(info["email"])
    except Exception as e:
        print(e, "Возникла ошибка при создании новой сессии")
        pass

    return jsonify({
        "message": "Авторизация успешна. Для пользователя была сформирована новая пара токенов для обслуживания",
        "access_token": couple["access_token"],
        "refresh_token": couple["refresh_token"]
    }), http_code.ok


# ==== categories ====

@app.route('/get_category_by_id', methods=['GET'])
@query_args(required="id")
async def get_category_by_id():
    """ Получение категории по id """
    id = request.args.get("id", type=int)
    result = await database.get_category_by_id(id)
    return jsonify({
        "category": result,
    }), http_code.ok


@app.route('/get_category_by_title', methods=['GET'])
@query_args(required="title")
async def get_category_by_title():
    """ Получение категории по title """
    title = request.args.get("title", type=str)
    result = await database.get_category_by_title(title)
    return jsonify({
        "category": result,
    }), http_code.ok


@app.route('/get_categories', methods=['GET'])
@query_args(possible="excluded_titles[]")
async def get_categories():
    """ Получение категории по title """
    excluded_titles = request.args.getlist("excluded_titles[]", type=str)
    result = await database.get_categories(excluded_titles)
    return jsonify({
        "categories": result,
    }), http_code.ok


# ==== collections ====

@app.route('/get_collection_by_id', methods=['GET'])
@query_args(required="id")
async def get_collection_by_id():
    """ Получение категории по id """
    id = request.args.get("id", type=int)
    result = await database.get_collection_by_id(id)
    return jsonify({
        "collection": result,
    }), http_code.ok


@app.route('/get_collection_by_title', methods=['GET'])
@query_args(required="title")
async def get_collection_by_title():
    """ Получение категории по title """
    title = request.args.get("title", type=str)
    result = await database.get_collection_by_title(title)
    return jsonify({
        "collection": result,
    }), http_code.ok


@app.route('/get_collections', methods=['GET'])
@query_args(possible="excluded_titles[]")
async def get_collections():
    """ Получение категории по title """
    excluded_titles = request.args.getlist("excluded_titles[]", type=str)
    result = await database.get_collections(excluded_titles)
    return jsonify({
        "collections": result,
    }), http_code.ok


# ==== products ====

@app.route('/get_filters', methods=['GET'])
@query_args(possible=("min_price", "max_price", "collection_ids[]", "category_ids[]", "options[]"))
async def get_filters():
    """ Получить, какие есть доступные фильтры при даннных ограничениях """
    min_price = request.args.get("min_price", None, type=int)
    max_price = request.args.get("max_price", None, type=int)

    collection_ids = request.args.getlist("collection_ids[]", type=int)
    category_ids = request.args.getlist("category_ids[]", type=int)
    options = request.args.getlist("options[]", type=str)
    options = [translitor.option_from_eng_to_ru(o) for o in options]

    filters = await database.get_products_filters(min_price, max_price, collection_ids, category_ids, options)

    for key in list(filters.keys()):
        if translitor.is_in_ru_titles(key):
            temp_data = filters[key]
            del filters[key]
            filters[translitor.ru_to_eng(key)] = temp_data
            print(translitor.ru_to_eng(key))

    return jsonify(
        filters
    ), http_code.ok


@app.route('/get_product_by_id', methods=['GET'])
@query_args(required="id")
async def get_product_by_id():
    """ Получение категории по id """
    id = request.args.get("id", type=int)
    result = await database.get_product_by_id(id)
    return jsonify({
        "product": result,
    }), http_code.ok


@app.route('/get_products', methods=['GET'])
@query_args(required=("page", "per_page"), possible=("order_by", "min_price", "max_price", "collection_ids[]", "category_ids[]", "options[]"))
async def get_products():
    """ 
        Получение товаров по фильтрам и с сортировкой. Текстовые поля регистр-зависимы
        -required:
    page:               номер страницы. Нумерация идет с единицы
    per_page:           количество товаров на странице

        -possible:
    order_by:           колонка, по которой вести сортировку. Если поставить минус перед именем, то будет сортировка по убыванию (например, "title" и "-title").
                        Доступные варианты: "price", "created_at", "title", "-price", "-created_at", "-title"
    min_price:          целое число - фильтр по минимальной цене
    max_price:          целое число - фильтр по максимальной цене
    collection_ids[]    список из id коллекций
    category_ids[]      список из id категорий
    options[]           список фильтрующих опций. Записывать через пробел "имя значений", например, "Цвет Золото", "Бренд VIVA LA VIKA", "Size 16"
    """
    page = request.args.get("page", type=int)
    per_page = request.args.get("per_page", type=int)
    if page <= 0:
        return jsonify({
            "message": "page должен быть больше 0",
        }), http_code.bad_request

    possible_order = ("price", "created_at", "title", "-price", "-created_at", "-title")
    order_by = request.args.get("order_by", None, type=str)
    if order_by not in possible_order and order_by is not None:
        return jsonify({
            "message": f"order может иметь только одно из следущих значений: {', '.join(possible_order)}",
        }), http_code.bad_request

    min_price = request.args.get("min_price", None, type=int)
    max_price = request.args.get("max_price", None, type=int)

    collection_ids = request.args.getlist("collection_ids[]", type=int)
    category_ids = request.args.getlist("category_ids[]", type=int)
    options = request.args.getlist("options[]", type=str)
    options = [translitor.option_from_eng_to_ru(o) for o in options]

    result = await database.get_products(order_by, page, per_page, min_price, max_price, collection_ids, category_ids, options)
    info = await database.get_products_filters(min_price, max_price, collection_ids, category_ids, options)

    for key in list(info.keys()):
        if translitor.is_in_ru_titles(key):
            temp_data = info[key]
            del info[key]
            info[translitor.ru_to_eng(key)] = temp_data
            print(translitor.ru_to_eng(key))
        
    return jsonify({
        "products": result
    }), http_code.ok



@app.route('/offer', methods=['POST'])
# Оформление заказа через мобильное приложение
def offer():
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })

@app.route('/add_towishlist', methods=['POST'])
async def add_towishlist():
    """ Добавление товара в вишлист. Если товар уже находится в вишлисте, ничего не происходит """
    info = await request.get_json()
    email = info['email']
    insales_id = info['insales_id']

    result  = await database.add_to_wishlist(email, insales_id)

    if result:
        message = 'Товар успешно добавление в вишлист'
    else:
        message = 'Товар уже был в вишлисте'
    
    return jsonify({
        'code': 200, 'message': message
        })


@app.route('/add_tocart', methods=['POST'])
async def add_tocart():
    """ Добавление товара в корзину. Если товар уже находится в корзине, ничего не происходит """
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })


@app.route('/delete_fromwishlist', methods=['POST'])
async def delete_fromwishlist():
    """ Удаление товара из вишлиста. Если товара не было, то ничего не происходит """
    info = await request.get_json()
    email = info['email']
    insales_id = info['insales_id']

    result  = await database.delete_from_wishlist(email, insales_id)

    if result:
        message = 'Товар успешно удален из вишлиста'
    else:
        message = 'Товара не было в вишлисте. Ничего не удалено'
    
    return jsonify({
        'code': 200, 'message': message
        })


@app.route('/delete_fromcart', methods=['POST'])
def delete_fromcart():
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })
    

@app.route('/get_products_fromwishlist', methods=['GET'])
async def get_fromwishlist():
    """ Получение всех товаров из вишлиста """
    try:
        info = await request.get_json()
        email = info['email']
        result = await database.get_wishlist_products(email)
        return jsonify({
            'code': 200,
            'message': result
            })
    except KeyError:
        return jsonify({
            'code': 400,
            'message': 'Invalid request data. Email field is missing.'
        })
    except TypeError as e:
        return jsonify({
            'code': 500,
            'message': str(e)
        })

@app.route('/get_fromcart', methods=['POST'])
# Получение товара из вишлиста
def get_fromcart():
    return jsonify({
        'code': 200, 'message': 'Тут будут категории'
        })

@app.route('/registration', methods=['POST'])
@query_args(required=("contact_name", "surname"), possible=("password", "password_confirmation", "birth_date", "email", "phone"))
# Получение товара из вишлиста
def regist():
    from insales_api import InsalesApi
    contact_name = request.args.get("contact_name", None, type=int)
    surname = request.args.get("surname", None, type=int)
# ,phone,email,password,password_confirmation,birth_date
    return InsalesApi.register()

# === Error handlers ===

@app.errorhandler(403)
def forbidden(e):
    return jsonify({
        "message": "Запрещено",
        "error": str(e)
    }), http_code.forbidden


@app.errorhandler(404)
def forbidden(e):
    return jsonify({
        "message": "Эндпоинт не найден",
        "error": str(e)
    }), http_code.not_found

@app.errorhandler(500)
def forbidden(e):
    return jsonify({
        "message": "Серверная ошибка",
        "error": str(e)
    }), http_code.not_found



# TODO Поменять ip адрес на 0.0.0.0
if __name__ == '__main__':
    app.run(host="localhost", debug=True, port=8080, threaded=True)