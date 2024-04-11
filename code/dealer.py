import Base

participant_count = Base.participant_count
bulletin_port = Base.bulletin_port

dealer = Base.Dealer(participant_count, "dealer", bulletin_port)

dealer.initialise_global_params()

dealer.generate_key()