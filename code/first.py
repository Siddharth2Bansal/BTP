from tinyec.ec import SubGroup, Curve
from random import randint

# class for global parameters
class params:
    q = 10531
    Q = None
    curve = None
    m = 100007
    number_of_parts = 10
    k = 5               # 5 secrets
    threshold = 7

# dummy hash functions, very weak
def hash_h(num, params):
    return num % params.m

def hash_q(point, params, r):
    return r * point


# setting up global params
global_params = params()
field = SubGroup(p=global_params.q, g=(1, 3), n=global_params.m, h=1)
global_params.curve = Curve(a=0, b=8, field=field, name='p1707')
global_params.Q = global_params.curve.g

# shareholder key generation
a = []
A = []
for i in range(global_params.number_of_parts):
    r = randint(0, global_params.m - 1)
    while r in a or r == 0:
        r = randint(0, global_params.m - 1)
    a.append(r)
    A.append(r * global_params.Q)

# key generation for dealer and combiner
r = randint(0, global_params.m - 1)
while r in a or r == 0:
    r = randint(0, global_params.m - 1)
a0 = r
A0 = a0 * global_params.Q

r = randint(0, global_params.m - 1)
while r in a or r == 0 or a0 * r % global_params.m == 0:
    r = randint(0, global_params.m - 1)
ac = r
Ac = ac * global_params.Q

# random integer for the sharing process
r = randint(1, global_params.m - 1)


# computing the combiner's secret
comb_sec = a0 * Ac
comb_sec = hash_q(comb_sec, global_params, r)
    # verifying the combiner's secret
comb_sec_c = ac * Ac
comb_sec_c = hash_q(comb_sec_c, global_params, r)

# assert comb_sec_c == comb_sec

print(f"Combiner's Secret is {comb_sec} and {comb_sec_c}")

b = []
b_p = []
I = []
I_p = []
X = []
X_p = []

# pseudo_share Computation
for i in range(global_params.number_of_parts):
    b.append(a0 * A[i])
    I.append(hash_q(b[i], global_params, r))
    X.append(hash_h(I[i].x ^ I[i].y, global_params))
    b_p.append(a[i] * A0)
    I_p.append(hash_q(b_p[i], global_params, r))
    X_p.append(hash_h(I_p[i].x ^ I_p[i].y, global_params))

# pseudo share verification

# Share Generation
# # Secret Publication after masking
secrets = []
pseudo_secrets = []
Z = []
for i in range(global_params.k):
    rand = randint(1, global_params.q - 1)
    S = rand * global_params.Q
    secrets.append(S)
    s = randint(1, global_params.m - 1)
    pseudo_secrets.append(s)
    W = s * global_params.Q
    Zi = W + S + comb_sec
    Z.append(Zi)

# # polynomial creation

coeffs = []
def f(x):
    val = 0
    i = 0
    for a in coeffs:
        val = (val + (a * (x**i)))% global_params.m
        i += 1
    return val 

if global_params.k <= global_params.threshold:
    for s in pseudo_secrets:
        coeffs.append(s)
    for i in range(global_params.threshold - global_params.k):
        coeffs.append(randint(1, global_params.m-1))
    
    # Computing public values
    Y = []
    for i in range(global_params.number_of_parts):
        y = f(X[i])
        Y.append(y * global_params.Q)
# missing the else case

