
# 路由的实现
class Routing(object):
    def __init__(self):
        self.routes = {}

    def route(self,path=None):
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator

    def __call__(self,environ,start_response):
        path = environ['PATH_INFO']
        if path in self.routes:
            start_response('404 Not Found', [('Content-Type', 'text/html; charset=utf-8')])
            return self.routes[path]()
        else:
            start_response('404 Not Found', [('Content-Type', 'text/html; charset=utf-8')])
            return '404 Not Found!'


