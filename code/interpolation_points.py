from tinyec.ec import SubGroup, Curve, Inf
from random import randint
from itertools import zip_longest


coeffs = [45, 34, 18, 24, 39, 11, 33, 56, 54, 45]
def f(x):
    val = 0
    i = 0
    for a in coeffs:
        val = (val + (a * (x**i)))% global_params.m
        i += 1
    return val 



# class for global parameters
class params:
    q = 113
    Q = None
    curve = None
    m = 59
    number_of_parts = 10
    k = 5               # 5 secrets
    threshold = 7

class Data:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

global_params = params()
field = SubGroup(p=global_params.q, g=(6, 2), n=global_params.m, h=1)
global_params.curve = Curve(a=1, b=8, field=field, name='p1707')
global_params.Q = global_params.curve.g

def function_from_values(solutions:list) -> list:
    a = [1]
    for x in solutions:
        b = [0]
        b.extend([-1*x*l for l in a])
        a = [sum(y) for y in zip_longest(a, b, fillvalue=0)]
    return a


def add_points(y_values):
    ans = 0
    for y_value in y_values:
        if ans == 0 or isinstance(ans, Inf):
            ans = y_value
        else:
            ans = y_value + ans
    return ans

def get_inverse(x, p):
    ans = 1
    for i in range(p-2):
        ans = (ans*x)%p
    return ans

def lagrange_interpolation(points, global_params):
    func = []
    func_without_y = []
    for point in points:
        temp = points.copy()
        temp.remove(point)
        p_i = [p.x for p in temp]
        p_i = function_from_values(p_i)
        denominator = 1
        for p in temp:
            denominator = denominator * (point.x - p.x)
        multiplier = get_inverse(denominator, global_params.m)
        p_i = [(x*multiplier) % global_params.m for x in p_i]
        p_i_without_y = [x*point.z for x in p_i]
        func_without_y = [add_points(y) for y in zip_longest(func_without_y, p_i_without_y, fillvalue=0)]
        p_i = [x*point.y for x in p_i]
        func = [add_points(y) for y in zip_longest(func, p_i, fillvalue=0)]
    func_without_y = [x%global_params.m for x in func_without_y]
    return func, func_without_y

# function -> Q * (x^2 + 4x - 6)

# points = [Data(1, -1*global_params.Q, -1), Data(2, 6*global_params.Q, 6), Data(0, 53*global_params.Q, 53)]

X = [18, 6, 13, 52, 46, 29, 40, 12, 43, 6]
points = [Data(x, f(x)*global_params.Q, f(x)) for x in X]
print(points)

reconstructed_function = lagrange_interpolation(points, global_params)
p1 = 59 * global_params.Q
p2 = 59 * global_params.Q
# print(p1+p2)
print("hopefully done and correct")