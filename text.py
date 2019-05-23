class A():
    def __init__(self):
        self.name=self.f.__name__
    
    def wrapp(f):
        return f
    def f(self):
        print ('a')
    def  cal(self):
        
        getattr(self,self.name)()

    @wrapp    
    def r(self):
        self.cal()

a = A()
a.r()
