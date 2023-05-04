from quart import Quart
from quart import render_template
from quart import request, jsonify



app = Quart(__name__) 


@app.route('/admin_products_list', methods=['GET', 'POST'])
async def admin_produts_list():
    return render_template('products_page.html')




@app.route('/admin_test', methods=['GET', 'POST'])
async def test_admin():
    return await render_template('index.html', name_admin = 'Administrator')


@app.route('/basic_table', methods=['GET', 'POST'])
async def basic_table():
    return await render_template('basic-table.html', name = 'Administrator')


@app.route('/admin', methods=['GET', 'POST']) #? Вход в административную панель
async def admin():
    if request.method == 'GET':
        
        return await render_template('admin_login.html')
    
    elif request.method == 'POST':
        name = await request.form.get('name')
        password = await request.form.get('password')

        if name == 'admin' and password == 'admin':
            return render_template('index.html')
        
        else:
            return jsonify(
                {
                'code': 200,
                'message': 'Повторите вход'
                }
            )