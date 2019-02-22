import asyncio
import logging
import pymysql
from DBUtils.PooledDB import PooledDB


def create_pool():
    global __pool
    return PooledDB(pymysql, 5, host="127.0.0.1", user='root',
                passwd='123456', db='testdb', port=3306, charset="utf8").connection()

def select(sql,args,size=None):
    #size可以决定取几条
    global __pool
    with __pool as conn:
        cur=conn.cursor()
        # 用参数替换而非字符串拼接可以防止sql注入
        print(sql.replace('?', '%s'), args)
        cur.execute(sql.replace('?','%s'),args)
        if size:
            rs=cur.fetchmany(size)
        else:
            rs=cur.fetchall()
        cur.close()
        return rs

def execute(sql,args):
    print(args)
    try:
        with (create_pool()) as conn:
            cur=conn.cursor()
            print(args)
            cur.execute(sql.replace('?', '%s'), args)
            affected=cur.rowcount
            cur.close()
    except BaseException as e:
        print(e)
    return affected

# 这个函数主要是把查询字段计数 替换成sql识别的?
# 比如说：insert into  `User` (`password`, `email`, `name`, `id`) values (?,?,?,?)  看到了么 后面这四个问号
def create_args_string(num):
    lol = []
    for n in range(num):
        lol.append('?')
    return (','.join(lol))


class Field(object):
    def __init__(self,name,column_type,primary_key,default):
        self.name=name # 字段名
        self.column_type=column_type # 字段数据类型
        self.primary_key=primary_key  # 是否是主键
        self.default=default  # 有无默认值
    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__,self.name)
class StringField(Field):
    def __init__(self,name=None,primary_key=False,default=None,ddl='varchar(100)'):
      super(StringField,self).__init__(name,ddl,primary_key,default)
  # 其它字段略，一个道理，一个模式

  # 让Model继承dict,主要是为了具备dict所有的功能，如get方法
  # metaclass指定了Model类的元类为ModelMetaClass


class ModelMetaClass(type):



    # 元类必须实现__new__方法，当一个类指定通过某元类来创建，那么就会调用该元类的__new__方法
    # 该方法接收4个参数
    # cls为当前准备创建的类的对象
    # name为类的名字，创建User类，则name便是User
    # bases类继承的父类集合,创建User类，则base便是Model
    # attrs为类的属性/方法集合，创建User类，则attrs便是一个包含User类属性的dict
    def __new__(cls, name, bases, attrs):
        # 因为Model类是基类，所以排除掉，如果你print(name)的话，会依次打印出Model,User,Blog，即
        # 所有的Model子类，因为这些子类通过Model间接继承元类
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)
        # 取出表名，默认与类的名字相同
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        # 用于存储所有的字段，以及字段值
        mappings = dict()
        # 仅用来存储非主键意外的其它字段，而且只存key
        fields = []
        # 仅保存主键的key
        primaryKey = None
        # 注意这里attrs的key是字段名，value是字段实例，不是字段的具体值
        # 比如User类的id=StringField(...) 这个value就是这个StringField的一个实例，而不是实例化
        # 的时候传进去的具体id值
        for k, v in attrs.items():
            # attrs同时还会拿到一些其它系统提供的类属性，我们只处理自定义的类属性，所以判断一下
            # isinstance 方法用于判断v是否是一个Field
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError("Douplicate primary key for field :%s" % key)
                    primaryKey = k
                else:
                    fields.append(k)
        # 保证了必须有一个主键
        if not primaryKey:
            raise RuntimeError("Primary key not found")
        # 这里的目的是去除类属性，为什么要去除呢，因为我想知道的信息已经记录下来了。
        # 去除之后，就访问不到类属性了，如图

        # 记录到了mappings,fields，等变量里，而我们实例化的时候，如
        # user=User(id='10001') ，为了防止这个实例变量与类属性冲突，所以将其去掉
        for k in mappings.keys():
            attrs.pop(k)
        # 以下都是要返回的东西了，刚刚记录下的东西，如果不返回给这个类，又谈得上什么动态创建呢？
        # 到此，动态创建便比较清晰了，各个子类根据自己的字段名不同，动态创建了自己
        # 下面通过attrs返回的东西，在子类里都能通过实例拿到，如self
        attrs['__mappings__'] = mappings
        attrs['__table__'] = tableName
        attrs['__primaryKey__'] = primaryKey
        attrs['__fields__'] = fields
        # 只是为了Model编写方便，放在元类里和放在Model里都可以
        attrs['__select__'] = "select %s ,%s from %s " % (
            primaryKey, ','.join(map(lambda f: '%s' % (mappings.get(f).name or f), fields)), tableName)
        attrs['__update__'] = "update %s set %s where %s=?" % (
            tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__insert__'] = "insert into %s (%s,%s) values (%s);" % (
            tableName, primaryKey, ','.join(map(lambda f: '%s' % (mappings.get(f).name or f), fields)),
            create_args_string(len(fields) + 1))
        attrs['__delete__'] = "delete from %s where %s= ? ;" % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaClass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    # 实现__getattr__与__setattr__方法，可以使引用属性像引用普通字段一样  如self['id']
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    # 貌似有点多次一举
    def getValue(self, key):
        value = getattr(self, key, None)
        return value

    # 取默认值，上面字段类不是有一个默认值属性嘛，默认值也可以是函数
    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                setattr(self, key, value)
        return value
        # 一步异步，处处异步，所以这些方法都必须是一个协程
        # 下面 self.__mappings__,self.__insert__等变量据是根据对应表的字段不同，而动态创建


    def save(self):
        print("aa")
        args = list(map(self.getValueOrDefault, self.__mappings__))
        print(args)
        return execute(self.__insert__, args)

    @asyncio.coroutine
    def remove(self):
        args = []
        args.append(self[self.__primaryKey__])
        print(self.__delete__)
        yield from execute(self.__delete__, args)

    @asyncio.coroutine
    def update(self, **kw):
        print("enter update")
        args = []
        for key in kw:
            if key not in self.__fields__:
                raise RuntimeError("field not found")
        for key in self.__fields__:
            if key in kw:
                args.append(kw[key])
            else:
                args.append(getattr(self, key, None))
        args.append(getattr(self, self.__primaryKey__))
        yield from execute(self.__update__, args)

    # 类方法
    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        rs = yield from select('%s where `%s`=?' % (cls.__select__, cls.__primaryKey__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])  # 返回的是一个实例对象引用

    @classmethod
    @asyncio.coroutine
    def findAll(cls, where=None, args=None):
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        rs = yield from select(' '.join(sql), args)
        return [cls(**r) for r in rs]

