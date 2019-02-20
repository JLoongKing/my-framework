from Source import server
from Source.Routing import Routing

app = Routing()
@app.route('/')
def index():
    html = "<h1>贪心学院，致力于AI教育！</h1>"

    return [html.encode(),]

@app.route('/hello')
def hello():
    html = "<h1>hello,贪心学院！！</h1>"

    return [html.encode(),]
server.start_server(app=app)