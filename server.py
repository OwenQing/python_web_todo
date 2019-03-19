import socket
import urllib.parse
from utils import log

from routes import (
    route_dict,
    # route_index,
)


from routes_todo import route_todo


class Request(object):

    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.headers = {}
        self.cookies = {}

    def add_cookies(self):
        """
        height=169; user=gua
        :return:
        """
        cookies = self.headers.get('Cookie', '')
        kvs = cookies.split(';')
        log('cookie', kvs)
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    def add_headers(self, header):
        """
        [
            'Accept-Language: zh-CN,zh;q=0.8'
            'Cookie: height=169; user=gua'
        ]
        """
        # 清空 headers
        self.headers = {}
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v
        # 清除 cookies
        self.cookies = {}
        self.add_cookies()

    # 把 body 里面的内容解析成字典
    def form(self):
        body = urllib.parse.unquote(self.body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f


request = Request()


def error(code=404):
    e = {
        404: b'HTTP/1.1 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
    }
    return e.get(code, b'')


def parse_path(path):
    """
     message=hello&author=gua
    {
        'message': 'hello',
        'author': 'gua',
    }
    传入一个
    返回path,和字典 query
    """
    index = path.find('?')
    if index == -1:
        return path, {}
    else:
        path, query_string = path.split('?', 1)
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return path, query


def response_for_path(path):
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    # parse_parse 用于把 path 和 query 分离
    path, query = parse_path(path)
    request.path = path
    request.query = query
    log('path and query', path, query)
    r = {
        # '/': route_index,

    }
    r.update(route_dict)
    r.update(route_todo)
    response = r.get(path, error)
    return response(request)


def run(host, port):
    with socket.socket() as s:
        s.bind((host, port))

        while True:
            s.listen(5)
            connection, address = s.accept()

            r = connection.recv(1024)
            r = r.decode('utf-8')
            log('原始请求', r)
            # 注意 split() 方法的使用
            # 这里是为了防止chrom 浏览器发送空请求，导致程序奔溃
            if len(r.split()) < 2:
                continue
            # 获取浏览器发来的请求的信息
            # path 直接从浏览器发过来的 HTTP 协议，解析的
            path = r.split()[1]
            log('-----这里是打印 path', path)
            request.method = r.split()[0]
            request.add_headers(r.split('\r\n\r\n', 1)[0].split('\r\n')[1:])
            request.body = r.split('\r\n\r\n', 1)[1]
            # 根据 route,来响应
            response = response_for_path(path)

            connection.sendall(response)
            connection.close()


if __name__ == '__main__':
    run('', 3000)
