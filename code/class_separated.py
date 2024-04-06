from tinyec.ec import SubGroup, Curve
from random import randint
from itertools import zip_longest

class Bulletin:
    def __init__(self, n, id):
        self.stored_values = {"global_params": {"number_of_parts": n}}
        self.stored_values["public"] = {}
        self.all_ids = ["bulletin", "dealer", "combiner"]
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
        self.all_ids = ["bulletin", "dealer", "combiner"]
        for i in range(n):
            self.all_ids.append(i)
        self.id = id


    def generate_key(self):
        self.private = randint(0, self.global_params["m"] - 1)
        self.public = self.private * self.global_params["Q"]
        while put_to_board(self.id, "public", self.public) == False:
            self.private = randint(0, self.global_params["m"] - 1)
            self.public = self.private * self.global_params["Q"]

class Dealer(Not_Bulletin):

    def initialise_global_params(self):
        self.global_params["m"] = 59
        self.global_params['k'] = 4
        self.global_params["w"] = 5
        self.global_params["q"] = 113
        field = SubGroup(p=self.global_params["q"], g=(6, 2), n=self.global_params["m"], h=1)
        self.global_params["curve"] = Curve(a=1, b=8, field=field, name='Sid')
        self.global_params["Q"] = self.global_params["curve"].g
        self.global_params["random_seed"] = randint(0, self.global_params["m"] - 1)
        put_to_board(self.id, "global_params", self.global_params)  

    def generate_key(self):
        self.private = randint(0, self.global_params["m"] - 1)
        self.public = self.private * self.global_params["Q"]
        put_to_board(self.id, "public", self.public)

class Combiner(Not_Bulletin):
    pass

class Participant(Not_Bulletin):
    pass


# the next part should have been in a config
participant_count = 10


# init the entities
bulletin_board = Bulletin(participant_count, "bulletin")
dealer = Dealer(participant_count, "dealer")
combiner = Combiner(participant_count, "combiner")
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

# verification of public keys stored in the bulletin (just to be sure)
assert(dealer.public == get_from_board("public", "dealer"))
assert(combiner.public == get_from_board("public", "combiner"))
for i in range(participant_count):
    assert(Participants[i].public == get_from_board("public", i))
