from wsgiref.simple_server import  make_server
from urllib import parse


https://www.jianshu.com/p/8f423aca2d75

https://www.cnblogs.com/i-honey/p/8110848.html


def demo_app(environ,start_response):
    from io import StringIO
    stdout = StringIO()
    print("Hello world!", file=stdout)
    print(file=stdout)
    h = environ.items()
    for k, v in h:
        print(k, '=', repr(v),"<br>", file=stdout)



    qstr = environ.get("QUERY_STRING")
    print(qstr)


    # ?id=5&name=ihoney&age=18,19
    print(parse.parse_qs(qstr))  # 字典,value为列表类型
    print(parse.parse_qsl(qstr))  # 二元组列表

    html = "<h1>北京欢迎你</h1>"
    start_response("200 OK", [('Content-Type', 'text/html; charset=utf-8')])
    return [html.encode(),stdout.getvalue().encode("utf-8")]

ip="127.0.0.1"
port=9999
server=make_server(ip,port,demo_app)
server.serve_forever()
server.server_close()