from tinyec.ec import SubGroup, Curve

class params:
    q = 25
    Q = None
    curve = None
    m = 18
    number_of_parts = 5

def hash_h(num, params):
    return num % params.m

def hash_q(point, params, r):
    return r * point

field = SubGroup(p=17, g=(15, 13), n=18, h=1)
global_params = params()
global_params.curve = Curve(a=0, b=7, field=field, name='p1707')
global_params.Q = global_params.curve.g

a = []
A = []
for i = range(global_params.number_of_parts):
    