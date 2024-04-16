import Base
# import pprint

# getting general configs from Base
wait_for_phases = Base.wait_for_phases
participant_count = Base.participant_count
bulletin_port = Base.bulletin_port

dealer = Base.Dealer(participant_count, "dealer", bulletin_port)

if wait_for_phases:
    input("press enter to continue to global parameter initialization.")
print("initializing global parameters and uploading to bulletin.\n")
dealer.initialise_global_params()

if wait_for_phases:
    input("press enter to continue to key generation.")
print("generating prvate/public key and the combiners secret.")
dealer.generate_key()
dealer.generate_combiner_secret()
print(f"private key: {dealer.private} and public key: {dealer.public}.\n")

if wait_for_phases:
    input("press enter to continue to pseudo share computation.")
print("generating pseudo shares and publishing verifiers for the participants.")
dealer.generate_pseudo_shares()
dealer.pseudo_share_verifier()
print(f"pseudo shares: {dealer.X}.\n")

if wait_for_phases:
    input("press enter to continue to secret sharing.")
print("generating random secret, pseudo secrets and shares for the participants.")
dealer.secret_share()
print(f"generated secrets: {dealer.secrets}.")

if wait_for_phases:
    input("press enter to continue to public share generation.")
print("generating public shares for the participants using the pseudo secrets.")
dealer.generate_coefficients()
dealer.generate_public_share()

dealer.signal_done()
print("Dealer part done!!")