from quart import Quart
from quart import jsonify
from quart import request
from quart import render_template
from server_helpers.session_factory import SSession
from server_helpers.token_factory import access_validation, refresh_validation, decrypt_and_get_email, access_creation, create_couple_by_email
from database import Database
from quart import abort



app = Quart(__name__)

ssession = SSession()
database = Database()

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



# Далее


# ? Данный метод можно смело применять при любом авторизованном запросе
async def token_process(access_token, refresh_token): # ? Функция, которая отвечает за проверку подленности токена
    # info = await request.get_json()
    result = await access_validation(access_token) 

    if result is not True:
        if not refresh_token or refresh_token == '' or len(refresh_token) == 0:
            return jsonify(
                {
                    'code': 203,
                    'message': 'Необходимо передать в запрос refresh_token. Он должен быть ненулевой для того, чтобы проверка прошла необходимым образом'
                }
            )
        result = await refresh_validation(refresh_token)

        if result is not True:
            return jsonify(
                {
                    'code': 401,
                    'message': 'Доступ закрыт. Необходимо авторизоваться повторно для создание новой пары refresh-access'
                }
            )
            
        else:

            new_access_token = await access_creation(access_token)
            return jsonify(
                {
                    'code': 201,
                    'message': 'Рефреш-токен действителен. Необходимо обновить access_token',
                    'access_token': new_access_token
                }
            )
        
    elif result:
        return True
    
    else:
        return False


### Start app. Configuration parametres. ###


@app.route('/')
def index():
    return jsonify(
        {
            'code': 200,
            'message': 'Start'
        }
    )



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
        access_token = request.headers.get('acess_token')
        refresh_token = request.headers.get('refresh_token')

        result = await token_process(access_token, refresh_token)
        if type(result) == bool:
            if result:
                pass
            elif not result: ...
        '''

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

            return jsonify(
                {
                    'code': 200,
                     'message': 'Авторизация успешна. Для пользователя была сформирована новая пара токенов для обслуживания',
                    'access_token': result['access_token'],
                    'refresh_token': result['refresh_token']
                }
            )
        
        else: 
            return jsonify(
                {
                    'code': 400,
                    'message': 'Доступ закрыт. Возможно, неправильно введены данные пользователя для входа. Перепроверьте вводимые данные'
                }
            )
    else:
        abort(400)

        
        

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


### Конец авторизации пользователя ###




### Регистрация ###
# ? Добавление нового пользователя в БД, выдача ему токенов. 



# То есть, если нажимают, летит запрос и почта подтвержается

app.route('email_code', methods=['GET', 'POST']) # Отправка кода на указанный email
def email_code(): #! Сделать авторизацию через email - страницу. Получение КОДА !!!! Нужно вводить код
    return jsonify(200)


@app.route('/email_code_repeat', methods=['GET', 'POST'])
def email_code_repeat(): # Повторная отправка email, если оно не пришло или было отправлено некорректно
    return jsonify(200)



@app.route('/email_confirm', methods=['GET', 'POST'])
def email_confirm():
    return jsonify(200) #! Подтверждение той электронной почты, на которую было отправлено писмьо. После того, как нажали



app.route('registration', methods=['POST'])
async def registration(): # Ввод личных данных при регистрации в приложении и запись данных в БД 
    if request.method == 'POST':

        info = await request.get_json()
        if not all(k in info for k in ('username', 'email', 'password', 'city')):
            return jsonify({'code': 400, 'message': 'Не хватает аргументов'})
        
        if await database.registration(info['username'], ['email'], ['password'], ['city'], ['billings'], ['wishlist']):

            result = await create_couple_by_email(info['email'])

            return jsonify(
                {
                    'code': 200,
                     'message': 'Пользователь с email: {} успешно зарегистрирован'.format(info['email']),
                    'access_token': result['access_token'],
                    'refresh_token': result['refresh_token']
                }
            )
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
        

    
### Конец методов работы с профилем пользователя ###



### Дополнительные методы ###
#? Рекомендации по уходу, о нас, магазины и тд. Все, что может быть дополнительным




        
















if __name__ == '__main__':
    app.run()