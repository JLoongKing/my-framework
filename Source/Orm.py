import asyncio
import logging
import pymysql
from DBUtils.PooledDB import PooledDB


def create_pool():
    return  PooledDB(pymysql, 5, host="localhost", user='root',
                passwd='123456', db='testdb', port=3306, charset="utf8").connection()

def doquery(sql):
    #size可以决定取几条
    conn=create_pool()
    cur=conn.cursor()
    # 用参数替换而非字符串拼接可以防止sql注入
    print(sql)
    cur.execute(sql)
    rs=cur.fetchall()
    conn.commit()
    cur.close()
    return rs

def execute(sql,args):
    try:
        conn = create_pool()
        cur=conn.cursor()
        cur.execute(sql.replace('?','%s'),args)
        conn.commit()
        affected=cur.rowcount
        cur.close()
    except BaseException as e:
        raise e
    return affected



#一、首先来定义Field类，它负责保存数据库表的字段名和字段类型：
class Field(object):
    def __init__(self, name, column_type):
        self.name = name
        self.column_type = column_type
    def __str__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.name)

class StringField(Field):
    def __init__(self, name):
        super(StringField, self).__init__(name, 'varchar(100)')

class IntegerField(Field):
    def __init__(self, name):
        super(IntegerField, self).__init__(name, 'bigint')

#二、定义元类，控制Model对象的创建
class ModelMetaclass(type):
    '''定义元类'''
    def __new__(cls, name, bases, attrs):
        if name=='Model':
            return super(ModelMetaclass,cls).__new__(cls, name, bases, attrs)
        mappings = dict()
        for k, v in attrs.items():
            # 保存类属性和列的映射关系到mappings字典
            if isinstance(v, Field):
                print('Found mapping: %s==>%s' % (k, v))
                mappings[k] = v
        for k in mappings.keys():
            #将类属性移除，使定义的类字段不污染User类属性，只在实例中可以访问这些key
            attrs.pop(k)
        attrs['__table__'] = name.lower() # 假设表名和为类名的小写,创建类时添加一个__table__类属性
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系，创建类时添加一个__mappings__类属性
        return super(ModelMetaclass,cls).__new__(cls, name, bases, attrs)

#三、编写Model基类
class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


    def save(self):
        print("调用了save")
        fields = []
        params = []
        args = []
        for k, v in self.__mappings__.items():
            fields.append(v.name)
            params.append('?')
            args.append(getattr(self, k, None))
        sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join(fields), ','.join(params))
        res = execute(sql,args)
        print(res)

    def get(self, field,param):
        print("调用了get")
        args = []
        fields = []
        for k, v in self.__mappings__.items():
            fields.append(v.name)

        for key in param:
            args.append(key)
        print('and'.join(args))
        for key in field:
            if key not in fields:
                raise RuntimeError("field not found")

        sql = 'select %s from %s where %s' % (','.join(fields),self.__table__, ' and '.join(args))
        res = doquery(sql)
        return res


    def update(self, field,param):
        print("enter update")
        args = []
        fields = []
        for key in field:
            fields.append(key)

        for key in param:
            args.append(key)
        print('and'.join(args))


        sql = 'update %s set %s where %s' % (self.__table__, ','.join(fields),' and '.join(args))
        print(sql)
        res = doquery(sql)
        return res

    def dele(self, param):
        print("enter update")
        args = []

        for key in param:
            args.append(key)
        print('and'.join(args))

        sql = 'DELETE FROM %s WHERE %s' % (self.__table__, ' and '.join(args))
        print(sql)
        res = doquery(sql)
        return res


