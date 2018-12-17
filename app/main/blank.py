from app.models import Tmachine
from ast import literal_eval

def table(name):
    tmachine = Tmachine.query.filter_by(id= name)
    for i in tmachine:
        states_d = i.states
        input_symbols_d = i.input_symbols
        tape_symbols_d = i.tape_symbols
        left_end_d = i.left_end
        transitions_d = i.transitions
        initial_state_d = i.initial_state
        blank_symbol_d = i.blank_symbol
        reject_state_d = i.reject_state
        final_states_d = i.final_states
    return blank_symbol_d
 
    

