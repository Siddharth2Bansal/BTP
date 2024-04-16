import Base
# import pprint
from tinyec.ec import SubGroup, Curve

# getting general configs from Base
wait_for_phases = Base.wait_for_phases
participant_count = Base.participant_count
bulletin_port = Base.bulletin_port

combiner = Base.Combiner(participant_count, -1, bulletin_port)

if wait_for_phases:
    input("press enter to continue to global parameter fetching.")
print("fetching global parameters from the bulletin board")
combiner.global_params = combiner.get_from_board("global_params")
field = SubGroup(p=combiner.global_params["q"], g=combiner.global_params["Q"], n=combiner.global_params["m"], h=1)
combiner.global_params["curve"] = Curve(a=combiner.global_params['a'], b=combiner.global_params['b'], field=field, name='Sid')
combiner.global_params["Q"] = combiner.global_params["curve"].g

if wait_for_phases:
    input("press enter to continue to key generation.")
print("generating prvate/public key and the combiners secret.")
combiner.generate_key()
combiner.generate_combiner_secret()

if wait_for_phases:
    input("press enter to continue to verifying identity with the participants.")
print("verifying identity with the participants.")
combiner.combiner_verifier()

if wait_for_phases:
    input("press enter to continue to fetching pseudo shares.")
print("fetching pseudo shares from the participants.")
combiner.get_pseudo_share()

print("verifying pseudo shares")
combiner.verify_pseudo_shares()

if wait_for_phases:
    input("press enter to continue to reconstruction of the secrets.")
print("reconstructing the secret using the pseudo shares.")
combiner.get_points()
reconstructed_secret = combiner.reconstrut_values(combiner.points)

print(f"the secrets reconstructed from the pseudo shares are: {reconstructed_secret}.")

combiner.signal_done()
print("Combiner part done!!")