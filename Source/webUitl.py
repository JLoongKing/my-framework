import socketserver, re, cgi, io, urllib.parse
from wsgiref.simple_server import WSGIServer

class Request(object):
    """保存客户端请求信息"""
    
    def __init__(self, env):
        self.env = env
        self.winput = env["wsgi.input"]
        self.method = env["REQUEST_METHOD"] # 获取请求方法(GET or POST)
        self.__attrs = {}
        self.attributes = {}
        self.encoding = "UTF-8"
 
    def __getattr__(self, attr):
        if(attr == "params" and "params" not in self.__attrs):
            fp = None
            if(self.method == "POST"):
                content = self.winput.read(int(self.env.get("CONTENT_LENGTH","0")))
                #fp = io.StringIO(content.decode(self.encoding))
                fp = io.StringIO(urllib.parse.unquote(content.decode("ISO-8859-1"),encoding=self.encoding))
                
            self.fs = cgi.FieldStorage(fp = fp, environ=self.env, keep_blank_values=1)# 创建FieldStorage
            self.params = {}
            for key in self.fs.keys():
                self.params[key] = self.fs[key].value
            self.__attrs["params"] = self.params
        return self.__attrs[attr]
 
class Response(object):
    """对客户端进行响应"""
 
    def __init__(self, start_response, write = None):
        self.encoding = "UTF-8"
        self.start_response = start_response
        self._write = write
 
    def write(self, string):
        """向流中写数据
            @param string:要写到流中的字符串
        """
        if(self._write is None):
            self._write = self.start_response("200 OK", [("Content-type","text/html;charset="+self.encoding)])
        self._write(string.encode(self.encoding).decode("ISO-8859-1"))
 
    def redirect(self, url):
        """跳转"""
        if(self._write is not None):
            raise AppException("响应流已写入数据，无法进行跳转。")
        self.start_response("302 OK", [("Location",url)])
