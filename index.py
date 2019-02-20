from Source import server
from Source.Routing import Routing

app = Routing()
@app.route('/')
def index():
    html = "<h1>贪心学院，致力于AI教育！</h1>"
    return [html.encode()]

@app.route('/hello')
def hello():
    request = app.request
    response = app.response
    print(request.params)
    name=request.params['name']
    html = "<h1>hello,贪心学院！！  我叫"+name+"</h1>"
    # html = "<h1>hello,贪心学院！！  我叫</h1>"
    # return [html.encode()]
    return response.write(html)

@app.route('/404')
def notfound():
    html = "<h1>您的页面可能去外星了！！</h1>"
    return [html.encode()]

server.start_server(app=app)