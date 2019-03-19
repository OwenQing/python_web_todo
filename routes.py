from utils import log
from models import User
import random

session = {}


def redirect(url):
    headers = {
        'Location': url,
    }
    r = response_with_headers(headers, 302) + '\r\n'
    return r.encode(encoding='utf-8')


def current_user(request):
    session_id = request.cookies.get('user', '')
    uname = session.get(session_id, '【游客】')
    return uname


def random_str():
    """
    生成一个随机字符串,seed的作用就是随机的从中选取字符。
    这个还是非常容易理解的
    """
    seed = 'dasiuo9fjkadsajnkd321432jijpojpodajsidj324235'
    s = ''
    for i in range(16):
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def response_with_headers(headers, code=200):
    """
Content-Type: text/html
Set-Cookie: user=gua
    """
    header = 'HTTP/1.1 {} VERY OK\r\n'.format(code)
    header += ''.join(['{}: {}\r\n'.format(k, v)
                       for k, v in headers.items()])
    return header


def template(name):
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def route_register(request):
    header = 'HTTP/1.1 210 VERY OK\r\nContent-Type: text/html\r\n'
    if request.method == 'POST':
        # HTTP BODY 如下
        # username=gw123&password=123
        # 经过 request.form() 函数之后会变成一个字典
        form = request.form()
        u = User.new(form)
        if u.validate_register():
            u.save()
            result = '注册成功<br> <pre>{}</pre>'.format(User.all())
        else:
            result = '用户名或者密码长度必须大于2'
    else:
        result = ''
    body = template('register.html')
    body = body.replace('{{result}}', result)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def route_login(request):
    headers = {
        'Content-Type': 'text/html',
    }
    if request.method == 'POST':
        form = request.form()
        u = User.new(form)
        if u.validate_login():
            session_id = random_str()
            session[session_id] = u.username
            headers['Set-Cookie'] = 'user={}'.format(session_id)

            result = '登录成功'
        else:
            result = '用户名或者密码错误'
    else:
        result = ''
    body = template('login.html')
    body = body.replace('{{result}}', result)
    r = response_with_headers(headers) + '\r\n' + body
    log('打印看看有没有设置 Cookie', r)
    return r.encode(encoding='utf-8')


route_dict = {
    '/login': route_login,
    '/register': route_register,
}
