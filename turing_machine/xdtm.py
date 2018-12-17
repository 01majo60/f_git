#!/usr/bin/env python3
"""Classes and methods for working with Turing machines."""

import copy

from turing_machine import tm
from turing_machine import exceptions
from turing_machine.tape import TMTape
from ast import literal_eval

class XDTM(tm.TM):
    """A more tape deterministic Turing machine."""
    def __init__(self, obj=None, **kwargs):
        """Initialize a complete Turing machine."""
        if isinstance(obj, XDTM):
            self._init_from_xdtm(obj)
        else:
            self._init_from_formal_params(**kwargs)

    def _init_from_formal_params(self, *, states, input_symbols, tape_symbols,left_end,
                                 transitions, initial_state, blank_symbol,reject_state,
                                 final_states):
        """Initialize a XDTM from the formal definition parameters."""
        self.states = states.copy()
        self.input_symbols = input_symbols.copy()
        self.tape_symbols = tape_symbols.copy()
        self.transitions = copy.deepcopy(transitions)
        self.initial_state = initial_state
        self.left_end = left_end
        self.blank_symbol = blank_symbol
        self.reject_state = reject_state
        self.final_states = final_states
        self.validate_self()

    def _init_from_xdtm(self, tm):
        """Initialize this XDTM as a deep copy of the given XDTM."""
        self.__init__(
            states=tm.states, input_symbols=tm.input_symbols,
            tape_symbols=tm.tape_symbols, transitions=tm.transitions,
            initial_state=tm.initial_state, blank_symbol=tm.blank_symbol,
            reject_state=tm.reject_state,final_states=tm.final_states,
            left_end=tm.left_end)

    def _validate_transition_state(self, transition_state):
        if transition_state not in self.states:
            raise exceptions.InvalidStateError(
                'stav ({}) v prechodovej funkcii nie je platný'.format(transition_state))

    def _validate_transition_symbols(self, state, paths):
        for tape_symbols in paths.keys():
            length = len(tape_symbols)
            for tape_symbol in tape_symbols:
                if tape_symbol not in self.tape_symbols:
                    raise exceptions.InvalidSymbolError(
                        'symbol {} v prechodovej funkcii pre stav {} nie je platný'.format(
                            tape_symbol, state))
        self._validate_transition_symbols_length(length,paths)

    def _validate_transition_symbols_length(self,length,paths):
        for tape_symbols in paths.keys():
            length1 = len(tape_symbols)
            if length != length1:
                    raise exceptions.Badcounttapes(
                        'zlý počet pások : ({}) v prechodovej funkcii'.format(tape_symbols))

    def _validate_transition_result_direction(self, result_direction):
        # L = left , R = right, S = state
        if not (result_direction == 'L' or result_direction == 'R' or result_direction == 'S'):
            raise exceptions.InvalidDirectionError(
                'výsledný smer prechodu ({}) nie je platný'.format(
                    result_direction))

    def _validate_transition_result(self, result):
        length = int((len(result) - 1)/2)
        result_state = result[0]
        if result_state not in self.states:
            raise exceptions.InvalidStateError(
                'stav ({}) nie je platný'.format(result_state))
        i = 1
        j = length +1
        while i <= length:
            result_symbol = result[i]
            result_direction = result[j]
            i += 1
            j += 1
            if result_symbol not in self.tape_symbols:
                raise exceptions.InvalidSymbolError(
                    'symbol ({}) nie je platný'.format(result_symbol))
            self._validate_transition_result_direction(result_direction)

    def _validate_transition_results(self, paths):
        for result in paths.values():
            length = len(result)
            self._validate_transition_result(result)
        self._validate_transition_length(length)

    def _validate_transition_length(self, length):
        for state, paths in self.transitions.items():
            for result in paths.values():
                length1 = len(result)
                if length != length1:
                    raise exceptions.Badcounttapes(
                        'zlý počet pások : ({}) v prechodovej funkcii'.format(result))
    
    def _validate_transitions(self):
        for state, paths in self.transitions.items():
            self._validate_transition_state(state)
            self._validate_transition_symbols(state, paths)
            self._validate_transition_results(paths)
            self._validate_left_end_direction_R(state,paths)

    def _validate_final_state_transitions(self):
        final_state = self.final_states
        if final_state in self.transitions:
            raise exceptions.FinalStateError(
                'Akceptujúci stav {} má definované prechody'.format(
                    final_state))
        
    def _validate_reject_state_transitions(self):
        reject_state = self.reject_state
        if reject_state in self.transitions:
            raise exceptions.RejectStateError(
                'Zamietajúci stav {} má definované prechody'.format(
                    reject_state))

                
    def _validate_left_end_direction_R(self,state, paths):
        for symbols in paths.keys():
            count = 1
            for symbol in symbols:
                if symbol in self.left_end:
                    tran = self.transitions.get(state).get(symbols)
                    length = int((len(tran)-1) /2)                   
                    symbol1 = tran[count]
                    direction1 = tran[count+length]
                    
                    if symbol1 != self.left_end and direction1 == 'L':
                        raise exceptions.LeftEndError(
                            'Lavá koncová značka {} je prepísaná symbolom {} a má smer prechodu {}'.format(
                                self.left_end, symbol1, direction1))                    
                    elif symbol1 != self.left_end:
                        raise exceptions.LeftEndError(
                            'Lavá koncová značka {} je prepísaná symbolom {}'.format(
                                self.left_end, symbol1))
                    elif direction1 == 'L':
                        raise exceptions.LeftEndError(
                            'Lavá koncová značka {} má smer prechodu {}'.format(
                                self.left_end,direction1))
                count += 1         
                


    def validate_self(self):
        """Return True if this XDTM is internally consistent."""
        self._validate_input_symbol_subset()
        self._validate_transitions()
        self._validate_initial_state()
        self._validate_initial_state_transitions()
        self._validate_nonfinal_initial_state()
        self._validate_reject_state()
        self._validate_reject_state_transitions()
        self._validate_final_states()
        self._validate_final_state_transitions()
        return True
    ######
    def _get_transition(self, state, tape_symbol):
        """Get the transiton tuple for the given state and tape symbol."""
        if (state in self.transitions and
                tape_symbol in self.transitions[state]):
            return self.transitions[state][tape_symbol]
        else:
            raise exceptions.RejectionError(
                'Zariadenie vstúpilo do nekoncovej konfigurácie pre ktorú nieje žiadny prechod ({}, {})'.format(state, tape_symbol))

    def _validate_input_yield(self, input_str):
        """
        Check if the given string is accepted by this Turing machine.
        Yield the current configuration of the machine at each step.
        """
        current_state = self.initial_state
        current_direction = None
        tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
        yield current_state, tape
        while current_state not in self.final_states:

            input_symbol = tape.read_symbol()
            (current_state, new_tape_symbol,
                current_direction) = self._get_transition(
                    current_state, input_symbol)
            tape.write_symbol(new_tape_symbol)
            tape.move(current_direction)

            yield current_state, tape

    ######upravit else
    def _get_transition1(self, state, tape_symbol):
        """Get the transiton tuple for the given state and tape symbol."""
        if (state in self.transitions and
                tape_symbol in self.transitions[state]):
            return self.transitions[state][tape_symbol],tape_symbol,state
        else:
            return state,tape_symbol
            

    def _validate_input_yield1(self, input_str):
        """
        Check if the given string is accepted by this Turing machine.

        Yield the current configuration of the machine at each step.
        """
        current_state = self.initial_state
        current_direction = None
        tapes = []
        current_directions = []
        input_symbols = []
        tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)

        for state, paths in self.transitions.items():
            for symbols in paths.keys():
                length = len(symbols)

        for i in range(length-1):
            tapes.append(i)
            current_directions.append(i)
            input_symbols.append(i)
        for i in tapes:
            tapes[i] = TMTape(self.left_end, blank_symbol=self.blank_symbol)
            current_directions[i] = None


        while current_state not in self.final_states and current_state not in self.reject_state:
            all_tapes = []
            all_tapes.append(tape)
            count = 0

            input_symbolss = ()
            input_symbolss += tape.read_symbol(),
            for i in tapes:
                all_tapes.append(i)
                input_symbolss += i.read_symbol(),
            
            try:
                (current),state1,current_state1 = self._get_transition1(
                        current_state, input_symbolss)
                current_state = current[count]
                count += 1
            # except ValueError if __validate_input_yield have not
            # 3 values (__validate_input_yield end in else)
            except ValueError:
                state,tape_symbol = self._get_transition1(
                        current_state, input_symbolss)
                yield state,tape_symbol, all_tapes, current
                break
            new_tape_symbol = current[count]
            count +=1
            tape.write_symbol(new_tape_symbol)
            
            for i in tapes:
                new_tape_symbol = current[count]
                count +=1
                i.write_symbol(new_tape_symbol)
                
            current_direction = current[count]
            count +=1
            tape.move(current_direction)
            for i in tapes:
                current_direction = current[count]
                count +=1
                i.move(current_direction)
            yield current_state1, state1, all_tapes, current

        input_symbolss = ()
        input_symbolss += tape.read_symbol(),
        for i in tapes:
            input_symbolss += i.read_symbol(),


        if current_state in self.final_states:
            yield current_state, input_symbolss, all_tapes, current
        elif current_state in self.reject_state:
            yield current_state, input_symbolss, all_tapes, current
            

