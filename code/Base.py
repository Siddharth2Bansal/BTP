from tinyec.ec import SubGroup, Curve
from random import randint
from itertools import zip_longest
import pprint
from time import time


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
    def __init__(self, n, id):
        self.stored_values = {"global_params": {"number_of_parts": n}}
        self.stored_values["public"] = {}
        self.all_ids = ["bulletin", "dealer", -1]
        for i in range(n):
            self.all_ids.append(i)
        self.id = id

    def get(self, type, id):
        if id == None:
            return self.stored_values[type]
        else:
            return self.stored_values[type][id]

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


# get from board to be updated
def get_from_board(type, id = None):
    return bulletin_board.get(type, id)

# put to board to be updated
def put_to_board(id, key, value):
    return bulletin_board.put(id, key, value)


class Not_Bulletin:
    def __init__(self, n, id):
        self.global_params = {"number_of_parts": n}
        self.all_ids = ["bulletin", "dealer", -1]
        for i in range(n):
            self.all_ids.append(i)
        self.id = id


    def generate_key(self):
        self.private = randint(1, self.global_params["m"] - 1)
        self.public = self.private * self.global_params["Q"]
        while put_to_board(self.id, "public", self.public) == False:
            self.private = randint(0, self.global_params["m"] - 1)
            self.public = self.private * self.global_params["Q"]

class Dealer(Not_Bulletin):

    def initialise_global_params(self):
        self.global_params["m"] = 59
        self.global_params['k'] = 2
        self.global_params["threshold"] = 3
        self.global_params["q"] = 113
        field = SubGroup(p=self.global_params["q"], g=(6, 2), n=self.global_params["m"], h=1)
        self.global_params["curve"] = Curve(a=1, b=8, field=field, name='Sid')
        self.global_params["Q"] = self.global_params["curve"].g
        self.global_params["random_seed"] = randint(0, self.global_params["m"] - 1)
        put_to_board(self.id, "global_params", self.global_params)  

    def generate_combiner_secret(self):
        combiner_public = get_from_board("public", -1)
        self.combiner_secret = self.private * combiner_public

    def generate_pseudo_shares(self):
        self.b = {}
        self.I = {}
        self.X = {}
        for i in self.all_ids:
            if i == "dealer" or i == -1 or i == "bulletin":
                continue
            participant_public = get_from_board("public", i)
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
            put_to_board(i, "u", u_i)
            put_to_board(i, "big_gamma", big_gamma_i)

    # coeffs contains a0, a1, a2 ... an
    def f(self, x):
        val = 0
        i = 0
        for a in self.coeffs:
            val = (val + (a * (x**i)))% dealer.global_params["m"]
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
            put_to_board(i, "Y", self.f(self.X[i]) * self.global_params["Q"])
        if self.global_params["k"] >= self.global_params["threshold"]:
            for i in range(self.global_params["k"] - self.global_params["threshold"]):
                r = randint(1, self.global_params["m"] - 1) 
                while r in self.X:
                    r = randint(1, self.global_params["m"] - 1)
                put_to_board(i, "public_r", r)
                put_to_board(i, "public_lambda", self.f(r) * self.global_params["Q"])
            
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
            put_to_board(i, "Z", Zi)



class Combiner(Not_Bulletin):
    def generate_combiner_secret(self):
        dealer_public = get_from_board("public", "dealer")
        self.combiner_secret = self.private * dealer_public

    def combiner_verifier(self):    
        for i in self.all_ids:
            if i == "dealer" or i == -1 or i == "bulletin":
                continue
            t = int(time())
            A = get_from_board("public", i)
            v = self.private * hash_h((i | -1 | t), self.global_params) * A
            put_to_board(i, "v", v)
            put_to_board(i, "t", t) 
    
    def get_pseudo_share(self):
        Ks = get_from_board("K")
        if(Ks.__len__() < self.global_params["threshold"]):
            Ks = get_from_board("K")
        self.X = {}
        for i in Ks.keys():
            A = get_from_board("public", i)
            I = Ks[i] + (self.private * A)
            self.X[i] = hash_h(I.x ^ I.y, self.global_params)

    def get_points(self):
        self.points = []
        if self.global_params["k"] >= self.global_params["threshold"]:
            for i in range(self.global_params["k"] - self.global_params["threshold"]):
                r = get_from_board("public_r", i)
                Lambda = get_from_board("public_lambda", i)
                self.points.append(Data(r, Lambda))
        for i in self.X.keys():
            y = get_from_board("Y", i)
            self.points.append(Data(self.X[i], y))

class Participant(Not_Bulletin):
    def compute_pseudo_share(self):
        self.b = self.private * get_from_board("public", "dealer")
        self.I = hash_q(self.b, self.global_params["random_seed"])
        self.X = hash_h(self.I.x ^ self.I.y, self.global_params)

    def verify_pseudo_share(self):
        u_i = get_from_board("u", self.id)
        big_gamma_i = get_from_board("big_gamma", self.id)
        dealer_public = get_from_board("public", "dealer")
        h_i = hash_h(self.X | self.id | big_gamma_i.x | big_gamma_i.y, self.global_params)
        assert(u_i * self.global_params["Q"] == big_gamma_i + (h_i * dealer_public))

    def verify_combiner(self):
        v = get_from_board("v", self.id)
        t = get_from_board("t", self.id)
        A = get_from_board("public", -1)
        assert(v == self.private * hash_h((self.id | -1 | t), self.global_params) * A)
    
    def transfer_pseudo_shares(self):
        A = get_from_board("public", -1)
        K = self.I - (self.private * A)
        put_to_board(self.id, "K", K)

# the next part should have been in a config
participant_count = 4


# init the entities
bulletin_board = Bulletin(participant_count, "bulletin")
dealer = Dealer(participant_count, "dealer")
combiner = Combiner(participant_count, -1)
Participants = [Participant(participant_count, i) for i in range(participant_count)]

# initialise the global params
dealer.initialise_global_params()

combiner.global_params = get_from_board("global_params")
for i in range(participant_count):
    Participants[i].global_params = get_from_board("global_params")

# public private key generation
dealer.generate_key()
combiner.generate_key()
for i in range(participant_count):
    Participants[i].generate_key()

# combiner secret computation
dealer.generate_combiner_secret()
combiner.generate_combiner_secret()

assert(dealer.combiner_secret == combiner.combiner_secret)

# pseudo share generation
dealer.generate_pseudo_shares()
    
# individually for each participant
for i in range(participant_count):
    Participants[i].compute_pseudo_share()

# pseudo share verification
dealer.pseudo_share_verifier()

for i in range(participant_count):
    Participants[i].verify_pseudo_share()


# should i implement combiner secret verification???
# only mentioned offhandly in the paper

dealer.secret_share()

dealer.generate_coefficients()

dealer.generate_public_share()


# combiner verification

combiner.combiner_verifier()

for i in range(participant_count):
    Participants[i].verify_combiner()


# transfer pseudo shares to combiner

for i in range(participant_count):
    Participants[i].transfer_pseudo_shares()

combiner.get_pseudo_share()

combiner.get_points()

pprint.pp(bulletin_board.stored_values)