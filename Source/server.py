from wsgiref.simple_server import  make_server
from urllib import parse

def demo_app(environ,start_response):
    from io import StringIO
    stdout = StringIO()
    print("Hello world!", file=stdout)
    print(file=stdout)
    h = environ.items()
    for k, v in h:
        print(k, '=', repr(v),"<br>", file=stdout)

    html = "<h1>贪心学院</h1>"
    start_response("200 OK", [('Content-Type', 'text/html; charset=utf-8')])
    return [html.encode(),stdout.getvalue().encode()]

def start_server(ip='127.0.0.1',port=8080,app=demo_app):
    server = make_server(ip, port, app)
    server.serve_forever()
    server.server_close()
