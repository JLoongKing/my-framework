# Web服务器网关接口（WSGI）是Web服务器软件和用Python编写的Web应用程序之间的标准接口。拥有标准接口可以轻松使用支持WSGI和多个不同Web服务器的应用程序。

# 只有Web服务器和编程框架的作者需要知道WSGI设计的每个细节和角落案例。您不需要了解WSGI的每个细节，只需安装WSGI应用程序或使用现有框架编写Web应用程序即可。

# wsgiref是WSGI规范的参考实现，可用于将WSGI支持添加到Web服务器或框架。它提供了用于操纵WSGI环境变量和响应头的实用程序，用于实现WSGI服务器的基类，为WSGI应用程序提供服务的演示HTTP服务器以及用于检查WSGI服务器和应用程序是否符合WSGI规范（PEP 333）的验证工具。

from wsgiref.simple_server import  make_server


def demo_app(environ,start_response):
    # 输出流
    from io import StringIO
    stdout = StringIO()
    # print("Hello world!", file=stdout)
    # 获取值
    h = environ.items()
    # 输出请求的参数key-value
    for k, v in h:
        print(k, '=', repr(v),"<br>",file=stdout)

    html = "<h1>贪心学院</h1>"
    start_response("200 OK", [('Content-Type', 'text/html; charset=utf-8')])
    return [html.encode(),stdout.getvalue().encode("utf-8")]

# 实现启动服务器
def start_server(ip='127.0.0.1',port=8080,app=demo_app):
    server = make_server(ip, port, app)
    # 循环一直监听端口处理请求
    server.serve_forever()
    server.server_close()
