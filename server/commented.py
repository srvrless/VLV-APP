


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