from functools import wraps

test_list: list = []

class aop(object):
    def __init__(self, aop_test_str):
        self.aop_test_str = aop_test_str
 
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print('before ' + self.aop_test_str)
            func(*args, **kwargs)
            print('after ' + self.aop_test_str)
 
        return wrapper
 
@aop('pppppp')
def hi(content: str):
    print(globals())
    print('hi', content)

if __name__ == '__main__':
    for i in dir(hi):
        if i.startswith('__'):
            print(i, ' --> ', getattr(hi, i))
    hi('az')