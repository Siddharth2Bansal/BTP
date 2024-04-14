import Base
from tinyec.ec import SubGroup, Curve
# import pprint

# getting general configs from Base
wait_for_phases = Base.wait_for_phases
bulletin_port = Base.bulletin_port

id = input("Enter the id of the participant: ")
id = int(id)
participant = Base.Participant(4, id, bulletin_port)

if wait_for_phases:
    input("press enter to continue to global parameter fetching.")
print("fetching global parameters from the bulletin board.")
participant.global_params = participant.get_from_board("global_params")
field = SubGroup(p=participant.global_params["q"], g=participant.global_params["Q"], n=participant.global_params["m"], h=1)
participant.global_params["curve"] = Curve(a=participant.global_params['a'], b=participant.global_params['b'], field=field, name='Sid')
participant.global_params["Q"] = participant.global_params["curve"].g

if wait_for_phases:
    input("press enter to continue to key generation.")
print("generating prvate/public key.")
participant.generate_key()

if wait_for_phases: 
    input("press enter to continue to pseudo share computation.")
print("generating pseudo shares and verifying them with the dealer.")
participant.compute_pseudo_share()

if wait_for_phases:
    input("press enter to continue to verification of combiner's identity.")
participant.verify_pseudo_share()

if wait_for_phases:
    input("press enter to continue to transferrence of pseudo shares to the combiner.")
print("if the combiner is verified, transfering the pseudo shares.")
if participant.verify_combiner():
    participant.transfer_pseudo_shares()

print("Participant part done!!")
