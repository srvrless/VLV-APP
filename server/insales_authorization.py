import requests

from aiohttp import ClientSession

async def login(email, password):
    url_login = "https://vivalavika.com/client_account/login"
    url_session = "https://vivalavika.com/client_account/session"
    domain = ".vivalavika.com"

    user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'

    session = requests.Session()
    r = session.get(url_login, headers = {
        'User-Agent': user_agent_val
    })

    session.headers.update({'Referer': url_login})

    session.headers.update({'User-Agent': user_agent_val})

    _xsrf = session.cookies.get('_xsrf', domain=domain)

    post_request = session.post(url_session, {
        'email': email,
        'password': password,
        '_xsrf':_xsrf
    })

    print(post_request)

    print(post_request.cookies)
    print(post_request.headers)
    print(post_request.url)


    #Вход успешно воспроизведен и мы сохраняем страницу в html файл
    with open("hh_success.html","w",encoding="utf-8") as f:
        f.write(post_request.text)