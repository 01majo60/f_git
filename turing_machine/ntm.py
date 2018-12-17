#!/usr/bin/env python3
"""Classes and methods for working with Turing machines."""

import copy

from turing_machine import tm
from turing_machine import exceptions
from turing_machine.tape import TMTape
import random 


class NTM(tm.TM):
    """A non-deterministic Turing machine."""
    def __init__(self, obj=None, **kwargs):
        """Initialize a complete Turing machine."""
        if isinstance(obj, NTM):
            self._init_from_ntm(obj)
        else:
            self._init_from_formal_params(**kwargs)

    def _init_from_formal_params(self, *, states, input_symbols, tape_symbols,left_end,
                                 transitions, initial_state, blank_symbol,reject_state,
                                 final_states):
        """Initialize a NTM from the formal definition parameters."""
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

    def _init_from_ntm(self, tm):
        """Initialize this NTM as a deep copy of the given NTM."""
        self.__init__(
            states=tm.states, input_symbols=tm.input_symbols,
            tape_symbols=tm.tape_symbols, transitions=tm.transitions,
            initial_state=tm.initial_state, blank_symbol=tm.blank_symbol,
            reject_state=tm.reject_state, final_states=tm.final_states,
            left_end=tm.left_end)

    def _validate_transition_state(self, transition_state):
        if transition_state not in self.states:
            raise exceptions.InvalidStateError(
                'stav ({}) v prechodovej funkcii nie je platný'.format(transition_state))

    def _validate_transition_symbols(self, state, paths):
        for tape_symbol in paths.keys():
            if tape_symbol not in self.tape_symbols:
                raise exceptions.InvalidSymbolError(
                    'symbol {} v prechodovej funkcii pre stav {} nie je platný'.format(
                        tape_symbol, state))

    def _validate_transition_result_direction(self, result_direction):
        if not (result_direction == 'L' or result_direction == 'R'):
            raise exceptions.InvalidDirectionError(
                'výsledný smer prechodu ({}) nie je platný'.format(
                    result_direction))

    def _validate_transition_result(self, result):
        for res in result:
            result_state, result_symbol, result_direction = res
            if result_state not in self.states:
                raise exceptions.InvalidStateError(
                    'stav ({}) nie je platný'.format(result_state))
            if result_symbol not in self.tape_symbols:
                raise exceptions.InvalidSymbolError(
                    'symbol ({}) nie je platný'.format(result_symbol))
            self._validate_transition_result_direction(result_direction)

    def _validate_transition_results(self, paths):
        for result in paths.values():
            self._validate_transition_result(result)

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
        for symbol in paths.keys():
            if symbol in self.left_end:               
                tran = self.transitions.get(state).get(symbol)
                for i in tran:
                    state1,symbol1,direction1 = i
                    if symbol1 != self.left_end and direction1 != 'R':
                        raise exceptions.LeftEndError(
                            'Lavá koncová značka {} je prepísaná symbolom {} a má smer prechodu {}'.format(
                                self.left_end, symbol1, direction1))                    
                    elif symbol1 != self.left_end:
                        raise exceptions.LeftEndError(
                            'Lavá koncová značka {} je prepísaná symbolom {}'.format(
                                self.left_end, symbol1))
                    elif direction1 != 'R':
                        raise exceptions.LeftEndError(
                            'Lavá koncová značka {} má smer prechodu {}'.format(
                                self.left_end,direction1))

    def validate_self(self):
        """Return True if this NTM is internally consistent."""
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

    def _length_transition(self, state, tape_symbol):
        zoznam = []
        if (state in self.transitions and
                tape_symbol in self.transitions[state]):
            trans = self.transitions[state][tape_symbol]
            j=1
            for i in trans:
                zoznam.append(j)
                j+=1
            return zoznam
        else:
            return zoznam
        
    def _get_transition(self, state, tape_symbol,possition):
        """Get the transiton tuple for the given state and tape symbol."""
        if (state in self.transitions and
                tape_symbol in self.transitions[state]):
            trans = self.transitions[state][tape_symbol]
            count = 1
            for i in trans:
                if count == int(possition):
                    return i
                count+=1
        else:
            return state, tape_symbol

        
    def _validate_input_yieldd(self, input_str):
        """return final configuration"""
        current_state = self.initial_state
        cross = None
        crossnumber = None
        zoznam = self._length_transition(current_state, self.left_end)
        cycle = False
        counter = 0
        counter1 = 0
        z1 = "" 
        current_direction = None
        tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
        while zoznam and counter < 200:
            if len(zoznam) > 1 and cross == None and crossnumber == None :
                cross = len(str(zoznam[-1]))
                crossnumber = str(zoznam[-1])[-1]
            counter +=1 
            zoznam1 = zoznam.pop(0)
            current_direction = None
            tape1 = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
            current_state = self.initial_state
            count = 0
            for possition in str(zoznam1):
                poss = possition
                count += 1
                input_symbol = tape1.read_symbol()
                if count == len(str(zoznam1)):
                    try:
                        (current_state, new_tape_symbol, current_direction) = self._get_transition(current_state, input_symbol,poss)
                        if current_state in self.final_states:
                            return zoznam1, cycle, cross, crossnumber
                        tape1.write_symbol(new_tape_symbol)
                        tape1.move(current_direction)
                        input_symbol = tape1.read_symbol()
                        z = self._length_transition(current_state, input_symbol)
                        if z and current_state != self.reject_state:
                            for i in z:
                                zoznam.append(int(str(zoznam1)+str(i)))
                    except ValueError:
                        (current_state, new_tape_symbol) = self._get_transition(current_state, input_symbol,poss)
                else:
                    (current_state, new_tape_symbol, current_direction) = self._get_transition(
                    current_state, input_symbol,poss)
                    tape1.write_symbol(new_tape_symbol)
                    tape1.move(current_direction)  
        else:
            current_state = self.initial_state
            zz = self._length_transition(current_state, input_str[0])
            current_direction = None
            tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
            input_symbol = tape.read_symbol()
            while True and counter1 < 200:
                counter1 +=1
                possition = 1
                if len(zz) > 1:
                    possition = random.randrange(1,len(zz)+1)
                z1+=str(possition)
                try:
                    (current_state, new_tape_symbol, current_direction) = self._get_transition(current_state, input_symbol,possition)    
                    tape.write_symbol(new_tape_symbol)
                    tape.move(current_direction)
                    input_symbol = tape.read_symbol()
                    zz = self._length_transition(current_state, input_symbol)
                    if current_state == self.reject_state:
                        return z1, cycle, cross, crossnumber
                except ValueError:
                    (current_state, new_tape_symbol) = self._get_transition(current_state, input_symbol,possition)
                    return z1, cycle, cross, crossnumber
            cycle = True
            return z1, cycle, cross, crossnumber


    def _validate_input_yield(self, input_str):
        """
        Yield the current configuration of the machine at each step.
        """
        final, cycle, cross, crossnumber = self._validate_input_yieldd(input_str)
        current_state = self.initial_state
        current_direction = None
        tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
        for i in str(final):
            input_symbol = tape.read_symbol()
            try:
                (current_state, new_tape_symbol, current_direction),state1,current_state1 = self._get_transition1(current_state, input_symbol,i)
            except ValueError:
                state,current_state = self._get_transition1(current_state, input_symbol,i)
                yield None,None,None, current_state, state,tape,final, cycle, cross, crossnumber
                break
            tape.write_symbol(new_tape_symbol)
            tape.move(current_direction)
            yield current_state, new_tape_symbol, current_direction,state1,current_state1,tape,final, cycle, cross, crossnumber
            
        input_symbol = tape.read_symbol()
        if current_state in self.final_states:
            yield None,None,None,input_symbol,current_state, tape,final, cycle, cross, crossnumber
        elif current_state in self.reject_state:
            yield None,None,None,input_symbol,current_state, tape,final, cycle, cross, crossnumber
        elif cycle == True:
            yield None,None,None,input_symbol,current_state, tape,final, cycle, cross, crossnumber
            
    def _get_transition1(self, state, tape_symbol,possition):
        """Get the transiton tuple for the given state and tape symbol."""
        if (state in self.transitions and
                tape_symbol in self.transitions[state]):
            trans = self.transitions[state][tape_symbol]
            count = 1
            for i in trans:
                if count == int(possition):
                    return i, tape_symbol, state
                count+=1
        else:
            return state, tape_symbol          

            
    def _validate_input_yield_final(self, input_str, final):
        current_state = self.initial_state
        current_direction = None
        cycle = False
        cycle1 = True
        crossnumber=[]
        tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
        for i in str(final):
            input_symbol = tape.read_symbol()
            z = self._length_transition(current_state, input_symbol)
            if z:
                crossnumber.append(str(z[-1])[-1])
            try:
                (current_state, new_tape_symbol, current_direction),state1,current_state1 = self._get_transition1(current_state, input_symbol,i)
            except ValueError:
                state,current_state = self._get_transition1(current_state, input_symbol,i)
                cycle1 = False
                yield None,None,None, current_state, state,tape, cycle, crossnumber
                break
            tape.write_symbol(new_tape_symbol)
            tape.move(current_direction)
            yield current_state, new_tape_symbol, current_direction,state1,current_state1,tape, cycle, crossnumber
            
        input_symbol = tape.read_symbol()
        crossnumber.append('1')
        if current_state in self.final_states:
            cycle1 = False
            yield None,None,None,input_symbol,current_state, tape, cycle, crossnumber
        elif current_state in self.reject_state:
            cycle1 = False
            yield None,None,None,input_symbol,current_state, tape, cycle, crossnumber
        elif cycle1:
            yield None,None,None,input_symbol,current_state, tape, cycle1, crossnumber


#### NONE_FINAL ####
        
    def _validate_input_yieldd_none_final(self, input_str, none_zoznam):
        """return final configuration"""
        current_state = self.initial_state
        current_direction = None
        tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)

        zoznam = []
        zoznam.append(none_zoznam)
        cross = None
        crossnumber = None
        cycle = False
        counter = 0
        counter1 = 0
        z1 = str(none_zoznam) 
        while zoznam and counter < 200:
            if len(zoznam) > 1 and cross == None and crossnumber == None :
                cross = len(str(zoznam[-1]))
                crossnumber = str(zoznam[-1])[-1]
            counter +=1 
            zoznam1 = zoznam.pop(0)
            current_direction = None
            tape_n = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
            current_state = self.initial_state
            count = 0
            for possition in str(zoznam1):
                poss = possition
                count += 1
                input_symbol = tape_n.read_symbol()
                if count == len(str(zoznam1)):
                    try:
                        (current_state, new_tape_symbol, current_direction) = self._get_transition(current_state, input_symbol,poss)
                        if current_state in self.final_states:
                            return zoznam1, cycle, cross, crossnumber
                        tape_n.write_symbol(new_tape_symbol)
                        tape_n.move(current_direction)
                        input_symbol = tape_n.read_symbol()
                        z = self._length_transition(current_state, input_symbol)
                        if z and current_state != self.reject_state:
                            for i in z:
                                zoznam.append(int(str(zoznam1)+str(i)))
                    except ValueError:
                        (current_state, new_tape_symbol) = self._get_transition(current_state, input_symbol,poss)
                else:
                    (current_state, new_tape_symbol, current_direction) = self._get_transition(
                    current_state, input_symbol,poss)
                    tape_n.write_symbol(new_tape_symbol)
                    tape_n.move(current_direction)  
        else:
            tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
            current_direction = None
            current_state = self.initial_state
            for i in str(none_zoznam):
                input_symbol = tape.read_symbol()
                try:
                    (current_state, new_tape_symbol, current_direction),state1,current_state1 = self._get_transition1(current_state, input_symbol,i)
                except ValueError:
                    state,current_state = self._get_transition1(current_state, input_symbol,i)
                    break
                tape.write_symbol(new_tape_symbol)
                tape.move(current_direction)

            input_symbol = tape.read_symbol()
            zz = self._length_transition(current_state, input_symbol)
            while True and counter1 < 200:
                counter1 +=1
                possition = 1
                if len(zz) > 1:
                    possition = random.randrange(1,len(zz)+1)
                z1+=str(possition)
                try:
                    (current_state, new_tape_symbol, current_direction) = self._get_transition(current_state, input_symbol,possition)    
                    tape.write_symbol(new_tape_symbol)
                    tape.move(current_direction)
                    input_symbol = tape.read_symbol()
                    zz = self._length_transition(current_state, input_symbol)
                    if current_state == self.reject_state:
                        return z1, cycle, cross, crossnumber
                except ValueError:
                    (current_state, new_tape_symbol) = self._get_transition(current_state, input_symbol,possition)
                    return z1, cycle, cross, crossnumber
            cycle = True
            return z1, cycle, cross, crossnumber


    def _validate_input_yield_none_final(self, input_str, zoznam):
        """
        Yield the current configuration of the machine at each step.
        """
        final, cycle, cross, crossnumber = self._validate_input_yieldd_none_final(input_str,zoznam)
        current_state = self.initial_state
        current_direction = None
        tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
        for i in str(final):
            input_symbol = tape.read_symbol()
            try:
                (current_state, new_tape_symbol, current_direction),state1,current_state1 = self._get_transition1(current_state, input_symbol,i)
            except ValueError:
                state,current_state = self._get_transition1(current_state, input_symbol,i)
                yield None,None,None, current_state, state,tape,final, cycle, cross, crossnumber
                break
            tape.write_symbol(new_tape_symbol)
            tape.move(current_direction)
            yield current_state, new_tape_symbol, current_direction,state1,current_state1,tape,final, cycle, cross, crossnumber
            
        input_symbol = tape.read_symbol()
        if current_state in self.final_states:
            yield None,None,None,input_symbol,current_state, tape,final, cycle, cross, crossnumber
        elif current_state in self.reject_state:
            yield None,None,None,input_symbol,current_state, tape,final, cycle, cross, crossnumber
        elif cycle == True:
            yield None,None,None,input_symbol,current_state, tape,final, cycle, cross, crossnumber
   
