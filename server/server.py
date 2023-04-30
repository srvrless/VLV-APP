from quart import Quart
from quart import jsonify
from quart import request
from quart import render_template



app = Quart(__name__)


### Start app. Configuration parameters. ###


@app.route('/')
def index():
    return jsonify(
        {
            'code': 200,
            'message': 'Start'
        }
    )



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



#TODO Проверка, чтобы администратор был авторизован: Защита от перехода поперек пользовательского сценария
#TODO Добавление нового баннера / редактирование тех баннеров, которые есть сейчас на странице
#! необходимо на эту страницу сначала выводить имебщиеся баннеры, чтобы их можно было редактировать
@app.route('/banner_edit', methods=['GET', 'POST']) # Функция взаимодействия (редактирования / добавления баннеров)
async def banner_edit():
    
    if request.method == 'GET': #! Доделать
        return render_template('banners.html') # ? переход на страницу добавления / редактирования баннеров
    
    if request.method == 'POST': #! Доделать
        return jsonify(200) # ? Добавление нового баннера (загрузка с компьютера). Заполнение полей бренда и названия


# TODO Добавлеие новых баннеров в БД
# TODO Вывод товаров из БД, чтобы их отображать на странице


@app.route('/get_banners', methods=['GET', 'POST']) # Получение баннеров (вывод)
def get_banners():
    return jsonify('DB information') #! 






### Main Routs ###


app.route('/login', methods=['GET', 'POST'])
def login():
    return()




### Регистрация ###
# ? Добавление нового пользователя в БД, выдача ему токенов. 


#TODO Нужно нажать на кнопку на почте, чтобы ее подтвердить. 
# То есть, если нажимают, летит запрос и почта подтвержается
#TODO Записать в БД статус электронной почты (код)
# TODO Отправка уведомдения о том, что код был неверный (если его ввели неверно)
app.route('email_code', methods=['GET', 'POST']) # Отправка кода на указанный email
def email_code(): #! Сделать авторизацию через email - страницу. Получение КОДА !!!! Нужно вводить код
    return jsonify(200)


@app.route('/email_code_repeat', methods=['GET', 'POST'])
def email_code_repeat(): # Повторная отправка email, если оно не пришло или было отправлено некорректно
    return jsonify(200)



@app.route('/email_confirm', methods=['GET', 'POST'])
def email_confirm():
    return jsonify(200) #! Подтверждение той электронной почты, на которую было отправлено писмьо. После того, как нажали



app.route('registration', methods=['GET', 'POST'])
async def registration(): # Ввод личных данных при регистрации в приложении и запись данных в БД 
    if request.method == 'POST':
        #! Запись в БД и создание токенов (всех необходимых)
        pass

    if request.method == 'GET':
        return jsonify(400) # Выдавать ошибку, если приходит такой запрос
    return jsonify(200)


app.route('/create_access_by_refresh', methods=['GET', 'POST']) #? Ручка обновления аксесс-токена
def create_access_by_refresh(): # GET 
    #TODO Передавать в контексте рефреш, по которому нужно будет все обновить
    return jsonify(200)


### Конец регистрации ###



### Сервисные специальные методы ###
# ? Нужны для принудительного игнорирования общего алгоритма


# ! Сервисный метод. Не использовать в общем алгоритме. Вызывается при возникновении ошибок, либо при принудительном игнорировании алгоритма
app.route('/create_refresh_by_email', methods=['GET', 'POST']) #? Отдельный метод для создания рефреш-токена
def create_refresh_by_email(): # GET 
    #TODO Передавать параметром email для создания нового рефреша
    return jsonify(200)


# ! Сервисный метод. Не использовать в общем алгоритме. Вызывается при возникновении ошибок, либо при принудительном игнорировании алгоритма
app.route('/create_access_by_email', methods=['GET', 'POST']) #? Отдельный метод для создания аксесс-токена
def create_access_by_email(): # GET 
    #TODO Передавать параметром email для создания нового аксесса
    return jsonify(200)


### Конец сервисных методов ###



### Авторизация ###
# ? Алгоримт входа пользователя в приложение. Проверка его токенов. 


app.route('login', methods=['GET', 'POST']) # ? Функция входа, а также принудительного входа, когда аксесс заканчивает свое действие. 
async def login(): # Авторизация в приложении пользователя. 
    if request.method == 'POST':
        #! Проверка по БД и произведение всех необходимых действий
        pass

    if request.method == 'GET':
        return jsonify(400) # Выдавать ошибку, если приходит такой запрос
    return jsonify(200)



### Конец авторизации пользователя ###











if __name__ == '__main__':
    app.run()