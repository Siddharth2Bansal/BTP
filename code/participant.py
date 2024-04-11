import Base
from tinyec.ec import SubGroup, Curve
import pprint

bulletin_port = Base.bulletin_port

id = input("Enter the id of the participant: ")
id = int(id)
participant = Base.Participant(4, id, bulletin_port)
participant.global_params = participant.get_from_board("global_params")
field = SubGroup(p=participant.global_params["q"], g=participant.global_params["Q"], n=participant.global_params["m"], h=1)
participant.global_params["curve"] = Curve(a=participant.global_params['a'], b=participant.global_params['b'], field=field, name='Sid')
participant.global_params["Q"] = participant.global_params["curve"].g

participant.generate_key()

participant.compute_pseudo_share()

participant.verify_pseudo_share()

# pprint.pprint(participant.global_params)