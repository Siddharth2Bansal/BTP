import Base
from tinyec.ec import SubGroup, Curve
import pprint

id = input("Enter the id of the participant: ")
participant = Base.Participant(4, id)
participant.global_params = participant.get_from_board("global_params")
field = SubGroup(p=participant.global_params["q"], g=participant.global_params["Q"], n=participant.global_params["m"], h=1)
participant.global_params["curve"] = Curve(a=participant.global_params['a'], b=participant.global_params['b'], field=field, name='Sid')
participant.global_params["Q"] = participant.global_params["curve"].g

participant.generate_key()

pprint.pprint(participant.global_params)