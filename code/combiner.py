import Base
import pprint
from tinyec.ec import SubGroup, Curve

participant_count = Base.participant_count
bulletin_port = Base.bulletin_port

combiner = Base.Combiner(participant_count, -1, bulletin_port)

combiner.global_params = combiner.get_from_board("global_params")
field = SubGroup(p=combiner.global_params["q"], g=combiner.global_params["Q"], n=combiner.global_params["m"], h=1)
combiner.global_params["curve"] = Curve(a=combiner.global_params['a'], b=combiner.global_params['b'], field=field, name='Sid')
combiner.global_params["Q"] = combiner.global_params["curve"].g

combiner.generate_key()

combiner.generate_combiner_secret()

combiner.combiner_verifier()

combiner.get_pseudo_share()

combiner.get_points()

reconstructed_secret = combiner.reconstrut_values(combiner.points)
pprint.pp(reconstructed_secret)