from models import Model
from routes import response_with_headers
from routes import redirect, current_user
from utils import template, log
from models import User


def login_required(route_function):
    def f(request):
        uname = current_user(request)
        u = User.find_by(username=uname)
        if u is None:
            return redirect('/login')
        return route_function(request)

    return f


# 继承自 Model 的 Todo 类
class Todo(Model):
    def __init__(self, form):
        self.id = form.get('id', None)
        self.title = form.get('title', '')
        self.user_id = int(form.get('user_id', -1))
        # 还应该增加 时间 等数据


def todo_index(request):
    uname = current_user(request)
    u = User.find_by(username=uname)
    if u is None:
        return redirect('/login')
    header = 'HTTP/1.1 200 VERY OK\r\nContent-Type:text/html\r\n'
    todolist = Todo.all()
    body = template('todo_index.html', todos=todolist)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def add(request):
    uname = current_user(request)
    u = User.find_by(username=uname)
    if u is None:
        return redirect('/login')
    title = request.form()
    log(title)
    user = Todo.new(title)
    user.save()
    return redirect('/todo')


def delete(request):
    uname = current_user(request)
    u = User.find_by(username=uname)
    if u is None:
        return redirect('/login')
    userid = request.query
    log('----------------------------历史的进程', userid)
    userid = int(userid['id'])
    Todo.delete(userid)
    return redirect('/todo')


route_todo = {
    '/todo': login_required(todo_index),
    '/todo/add': login_required(add),
    '/delete': login_required(delete),
}
