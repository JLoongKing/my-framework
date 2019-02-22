from Source import server
from Source.Routing import Routing
from Source.Orm import *

#最后，我们使用定义好的ORM接口，使用起来非常的简单。
class User(Model):
    # 定义类的属性到列的映射：
    id = IntegerField('id')
    name = StringField('name')



app = Routing()
@app.route('/')
def index():
    html = "<h1>贪心学院，致力于AI教育！</h1>"
    return [html.encode()]

@app.route('/hello')
def hello():
    # 存入数据库:
    # 创建一个实例：
    # u = User(id=12345, name='Michael')
    # 保存到数据库：
    # u.save()
    # u=User()
    # re=u.get(["name"],["id=12345","name='Michael'"])
    # print(re)
    # u=User()
    # re=u.update(["id=1","name='greedy'"],["id=12345"])
    # print(re)
    u=User()
    re=u.dele(["id=1"])
    print(re)
    # html = "<h1>hello,贪心学院！！  我叫</h1>"
    # return [html.encode()]
    html = "<h1>您的页面可能去外星了！！</h1>"
    return [html.encode()]

@app.route('/404')
def notfound():
    html = "<h1>您的页面可能去外星了！！</h1>"
    return [html.encode()]

server.start_server(app=app)