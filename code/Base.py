from tinyec.ec import SubGroup, Curve, Inf, Point
from random import randint
from itertools import zip_longest
import pprint
import time
import socket
import json

# dummy hash functions, very weak
def hash_h(num, params):
    return num % params["m"]

def hash_q(point, r):
    return r * point


class Data:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Bulletin:
    def __init__(self, n, id, port = 12345):
        self.stored_values = {"global_params": {"number_of_parts": n}}
        self.stored_values["public"] = {}
        self.all_ids = ["bulletin", "dealer", -1]
        for i in range(n):
            self.all_ids.append(i)
        self.id = id
        self.port = port
        self.socket = socket.socket()
        self.socket.bind(('', self.port))
        self.socket.listen(7)

    def get(self, type, id):
        if id == None:
            if type not in self.stored_values.keys():
                return 'not present'
            return self.stored_values[type]
        else:
            if type in self.stored_values.keys():
                if id in self.stored_values[type].keys():
                    return self.stored_values[type][id]
            return 'not present'
        
    def verify_key(self, id, key):
        flag = True
        for public_key in self.stored_values["public"]:
            if public_key == key:
                flag = False
        return flag

    def put(self, id, type, value):
        if type == "global_params":
            self.stored_values[type] = value
        elif type == "public":
            if self.verify_key(id, value):
                self.stored_values[type][id] = value
            else:
                return False
        else:
            if type not in self.stored_values.keys():
                self.stored_values[type] = {}
            self.stored_values[type][id] = value
        return True
 

class Not_Bulletin:
    def __init__(self, n, id, port = 12345):
        self.global_params = {"number_of_parts": n}
        self.all_ids = ["bulletin", "dealer", -1]
        for i in range(n):
            self.all_ids.append(i)
        self.id = id
        self.bulletin_port = port


    def generate_key(self):
        self.private = randint(1, self.global_params["m"] - 1)
        self.public = self.private * self.global_params["Q"]
        while self.put_to_board(self.id, "public", (self.public.x, self.public.y)) == False:
            self.private = randint(0, self.global_params["m"] - 1)
            self.public = self.private * self.global_params["Q"]

    # get from board to be updated
    def get_from_board(self, type, id = None, ip = '127.0.0.1'):
        self.socket = socket.socket()
        self.socket.connect((ip, self.bulletin_port))
        self.socket.send(json.dumps({"action":"get", "id": id, "type": type}).encode())
        data = self.socket.recv(2048).decode()
        data = json.loads(data)
        self.socket.close()
        while data == 'not present':
            time.sleep(5)
            self.socket = socket.socket()
            self.socket.connect((ip, self.bulletin_port))
            self.socket.send(json.dumps({"action":"get", "id": id, "type": type}).encode())
            data = self.socket.recv(2048).decode()
            data = json.loads(data)
            self.socket.close()
        return data
        # return bulletin_board.get(type, id)

    # put to board to be updated
    def put_to_board(self, id, key, value, ip = '127.0.0.1'):
        self.socket = socket.socket()
        self.socket.connect((ip, self.bulletin_port))
        self.socket.send(json.dumps({"action":"put", "id": id, "key": key, "value": value}).encode())
        if self.socket.recv(2048).decode() == "False":
            self.socket.close()
            return False
        self.socket.close()
        return True
        # self.socket.send("put")
        # return bulletin_board.put(id, key, value)


class Dealer(Not_Bulletin):

    def initialise_global_params(self):
        self.global_params["m"] = 59
        self.global_params['k'] = 2
        self.global_params["threshold"] = 3
        self.global_params["q"] = 113
        self.global_params["Q"] = (6, 2)
        self.global_params['a'] = 1
        self.global_params['b'] = 8
        self.global_params["random_seed"] = randint(0, self.global_params["m"] - 1)
        self.put_to_board(self.id, "global_params", self.global_params)
        field = SubGroup(p=self.global_params["q"], g=self.global_params["Q"], n=self.global_params["m"], h=1)
        self.global_params["curve"] = Curve(a=self.global_params['a'], b=self.global_params['b'], field=field, name='Sid')
        self.global_params["Q"] = self.global_params["curve"].g

    def generate_combiner_secret(self):
        combiner_public = self.get_from_board("public", -1)
        combiner_public = Point(self.global_params["curve"], combiner_public[0], combiner_public[1])
        self.combiner_secret = self.private * combiner_public

    def generate_pseudo_shares(self):
        self.b = {}
        self.I = {}
        self.X = {}
        for i in self.all_ids:
            if i == "dealer" or i == -1 or i == "bulletin":
                continue
            participant_public = self.get_from_board("public", i)
            participant_public = Point(self.global_params["curve"], participant_public[0], participant_public[1])
            self.b[i] = (self.private * participant_public)
            self.I[i] = (hash_q(self.b[i], self.global_params["random_seed"]))
            self.X[i] = (hash_h(self.I[i].x ^ self.I[i].y, self.global_params))

    def pseudo_share_verifier(self):
        for i in self.all_ids:
            if i == "dealer" or i == -1 or i == "bulletin":
                continue
            small_gamma_i = randint(1, self.global_params["m"] - 1)
            big_gamma_i = small_gamma_i * self.global_params["Q"]
            h_i = hash_h(self.X[i] | i | big_gamma_i.x | big_gamma_i.y, self.global_params)
            u_i = small_gamma_i + (h_i * self.private)
            self.put_to_board(i, "u", u_i)
            self.put_to_board(i, "big_gamma", (big_gamma_i.x, big_gamma_i.y))

    # coeffs contains a0, a1, a2 ... an
    def f(self, x):
        val = 0
        i = 0
        for a in self.coeffs:
            val = (val + (a * (x**i)))% self.global_params["m"]
            i += 1
        return val 

    def generate_coefficients(self):
        self.coeffs = []
        for s in self.pseudo_secrets:
            self.coeffs.append(s)
        if self.global_params["k"] <= self.global_params["threshold"]:
            for _ in range(self.global_params["threshold"] - self.global_params["k"]):
                self.coeffs.append(randint(1, self.global_params["m"] - 1))

    def generate_public_share(self):
        for i in self.all_ids:
            if i == "dealer" or i == -1 or i == "bulletin":
                continue
            Y = self.f(self.X[i]) * self.global_params["Q"]
            self.put_to_board(i, "Y", (Y.x, Y.y))
        if self.global_params["k"] >= self.global_params["threshold"]:
            for i in range(self.global_params["k"] - self.global_params["threshold"]):
                r = randint(1, self.global_params["m"] - 1) 
                while r in self.X:
                    r = randint(1, self.global_params["m"] - 1)
                self.put_to_board(i, "public_r", (r.x, r.y))
                lamb = self.f(r) * self.global_params["Q"]
                self.put_to_board(i, "public_lambda", (lamb.x, lamb.y))
            
    def secret_share(self):        
        self.secrets = []
        self.pseudo_secrets = []
        for i in range(self.global_params["k"]):
            rand = randint(1, self.global_params["q"] - 1)
            S = rand * self.global_params["Q"]
            self.secrets.append(S)
            s = randint(1, self.global_params["m"] - 1)
            self.pseudo_secrets.append(s)
            W = s * self.global_params["Q"]
            Zi = W + S + self.combiner_secret
            self.put_to_board(i, "Z", (Zi.x, Zi.y))



class Combiner(Not_Bulletin):
    def generate_combiner_secret(self):
        dealer_public = self.get_from_board("public", "dealer")
        dealer_public = Point(self.global_params['curve'], dealer_public[0], dealer_public[1])
        self.combiner_secret = self.private * dealer_public

    def combiner_verifier(self):    
        for i in self.all_ids:
            if i == "dealer" or i == -1 or i == "bulletin":
                continue
            t = int(time.time())
            A = self.get_from_board("public", i)
            A = Point(self.global_params['curve'], A[0], A[1])
            v = self.private * hash_h((i | -1 | t), self.global_params) * A
            self.put_to_board(i, "v", (v.x, v.y))
            self.put_to_board(i, "t", t) 
    
    def get_pseudo_share(self):
        Ks = self.get_from_board("K")
        if(Ks.__len__() < self.global_params["threshold"]):
            Ks = self.get_from_board("K")
        for i in Ks.keys():
            Ks[i] = Point(self.global_params['curve'], Ks[i][0], Ks[i][1])
        self.X = {}
        for i in Ks.keys():
            A = self.get_from_board("public", i)
            A = Point(self.global_params['curve'], A[0], A[1])
            I = Ks[i] + (self.private * A)
            self.X[i] = hash_h(I.x ^ I.y, self.global_params)
        temp = self.X
        self.X = {}
        for i in temp.keys():
            if i == self.global_params["threshold"]:
                break
            self.X[i] = temp[i]


    def get_points(self):
        self.points = []
        if self.global_params["k"] >= self.global_params["threshold"]:
            for i in range(self.global_params["k"] - self.global_params["threshold"]):
                r = self.get_from_board("public_r", i)
                r = Point(self.global_params['curve'], r[0], r[1])
                Lambda = self.get_from_board("public_lambda", i)
                Lambda = Point(self.global_params['curve'], Lambda[0], Lambda[1])
                self.points.append(Data(r, Lambda))
        for i in self.X.keys():
            y = self.get_from_board("Y", i)
            y = Point(self.global_params['curve'], y[0], y[1])
            self.points.append(Data(self.X[i], y))
        

    def function_from_values(self, solutions:list) -> list:
        a = [1]
        for x in solutions:
            b = [0]
            b.extend([-1*x*l for l in a])
            a = [sum(y) for y in zip_longest(a, b, fillvalue=0)]
        return a


    def add_points(self, y_values):
        ans = 0
        for y_value in y_values:
            if ans == 0 or isinstance(ans, Inf):
                ans = y_value
            else:
                ans = y_value + ans
        return ans

    def get_inverse(self, x, p):
        ans = 1
        for _ in range(p-2):
            ans = (ans*x)%p
        return ans

    def lagrange_interpolation(self, points, global_params):
        func = []
        for point in points:
            temp = points.copy()
            temp.remove(point)
            p_i = [p.x for p in temp]
            p_i = self.function_from_values(p_i)
            denominator = 1
            for p in temp:
                denominator = denominator * (point.x - p.x)
            multiplier = self.get_inverse(denominator, global_params["m"])
            p_i = [(x*multiplier) % global_params["m"] for x in p_i]
            p_i = [x*point.y for x in p_i]
            func = [self.add_points(y) for y in zip_longest(func, p_i, fillvalue=0)]
        func.reverse()
        return func

    def reconstrut_values(self, points):
        reconstructed_function = self.lagrange_interpolation(points, self.global_params)
        self.reconstruted_secrets = []
        for i in range(self.global_params["k"]):
            Z = self.get_from_board("Z", i)
            Z = Point(self.global_params['curve'], Z[0], Z[1])
            self.reconstruted_secrets.append(Z - reconstructed_function[i] - self.combiner_secret)
        return self.reconstruted_secrets

class Participant(Not_Bulletin):
    def compute_pseudo_share(self):
        dealer_public = self.get_from_board("public", "dealer")
        dealer_public = Point(self.global_params['curve'], dealer_public[0], dealer_public[1])
        self.b = self.private * dealer_public
        self.I = hash_q(self.b, self.global_params["random_seed"])
        self.X = hash_h(self.I.x ^ self.I.y, self.global_params)

    def verify_pseudo_share(self):
        u_i = self.get_from_board("u", self.id)
        big_gamma_i = self.get_from_board("big_gamma", self.id)
        big_gamma_i = Point(self.global_params['curve'], big_gamma_i[0], big_gamma_i[1])
        dealer_public = self.get_from_board("public", "dealer")
        dealer_public = Point(self.global_params['curve'], dealer_public[0], dealer_public[1])
        h_i = hash_h(self.X | self.id | big_gamma_i.x | big_gamma_i.y, self.global_params)
        assert(u_i * self.global_params["Q"] == big_gamma_i + (h_i * dealer_public))

    def verify_combiner(self):
        v = self.get_from_board("v", self.id)
        v = Point(self.global_params['curve'], v[0], v[1])
        t = self.get_from_board("t", self.id)
        A = self.get_from_board("public", -1)
        A = Point(self.global_params['curve'], A[0], A[1])
        assert(v == self.private * hash_h((self.id | -1 | t), self.global_params) * A)
    
    def transfer_pseudo_shares(self):
        A = self.get_from_board("public", -1)
        A = Point(self.global_params['curve'], A[0], A[1])
        K = self.I - (self.private * A)
        self.put_to_board(self.id, "K", (K.x, K.y))

# # the next part should have been in a config
# participant_count = 4


# # init the entities
# bulletin_board = Bulletin(participant_count, "bulletin")
# dealer = Dealer(participant_count, "dealer")
# combiner = Combiner(participant_count, -1)
# Participants = [Participant(participant_count, i) for i in range(participant_count)]

# # initialise the global params
# dealer.initialise_global_params()

# combiner.global_params = combiner.get_from_board("global_params")
# for i in range(participant_count):
#     Participants[i].global_params = Participants[i].get_from_board("global_params")

# # public private key generation
# dealer.generate_key()
# combiner.generate_key()
# for i in range(participant_count):
#     Participants[i].generate_key()

# # combiner secret computation
# dealer.generate_combiner_secret()
# combiner.generate_combiner_secret()

# assert(dealer.combiner_secret == combiner.combiner_secret)

# # pseudo share generation
# dealer.generate_pseudo_shares()
    
# # individually for each participant
# for i in range(participant_count):
#     Participants[i].compute_pseudo_share()

# # pseudo share verification
# dealer.pseudo_share_verifier()

# for i in range(participant_count):
#     Participants[i].verify_pseudo_share()


# # should i implement combiner secret verification???
# # only mentioned offhandly in the paper
################################### done till here
# dealer.secret_share()

# dealer.generate_coefficients()

# dealer.generate_public_share()


# # combiner verification

# combiner.combiner_verifier()

# for i in range(participant_count):
#     Participants[i].verify_combiner()


# # transfer pseudo shares to combiner

# for i in range(participant_count):
#     Participants[i].transfer_pseudo_shares()

# combiner.get_pseudo_share()

# combiner.get_points()

# reconstructed_secrets = combiner.reconstrut_values(combiner.points)

# pprint.pp(dealer.secrets)
# pprint.pp(reconstructed_secrets)


# CONFIGS
participant_count = 3
bulletin_port = 12341