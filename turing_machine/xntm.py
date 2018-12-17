#!/usr/bin/env python3
"""Classes and methods for working with Turing machines."""

import copy

from turing_machine import tm
from turing_machine import exceptions
from turing_machine.tape import TMTape
import random
from ast import literal_eval


class XNTM(tm.TM):
    """A more tape non-deterministic Turing machine."""
    def __init__(self, obj=None, **kwargs):
        """Initialize a complete Turing machine."""
        if isinstance(obj, XNTM):
            self._init_from_xntm(obj)
        else:
            self._init_from_formal_params(**kwargs)

    def _init_from_formal_params(self, *, states, input_symbols, tape_symbols,left_end,
                                 transitions, initial_state, blank_symbol,reject_state,
                                 final_states):
        """Initialize a XNTM from the formal definition parameters."""
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

    def _init_from_xntm(self, tm):
        """Initialize this XNTM as a deep copy of the given NTM."""
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
        while i<= length:
            result_symbol = result[i]
            result_direction = result[j]
            i += 1
            j += 1
            if result_symbol not in self.tape_symbols:
                raise exceptions.InvalidSymbolError(
                    'symbol ({}) nie je platný'.format(result_symbol))
            self._validate_transition_result_direction(result_direction)

    def _validate_transition_results(self, paths):
        for results in paths.values():
            for result in results:
                length = len(result)
                self._validate_transition_result(result)
        self._validate_transition_length(length)


    def _validate_transition_length(self, length):
        for state, paths in self.transitions.items():
            for results in paths.values():
                for result in results:
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
                    for i in tran:
                        length = int((len(i)-1) /2) 
                        symbol1 = i[count]
                        direction1 = i[count+length]

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
                count +=1
    
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
                    return i,None, None
                count+=1
        else:
            return state, tape_symbol

        
    def _validate_input_yieldd(self, input_str):
        """return final configuration"""
        current_state = self.initial_state
        cross = None
        crossnumber = None
        
        cycle = False
        counter = 0
        counter1 = 0
        z1 = "" 
        current_direction = None
        
        tapes = []
        current_directions = []
        input_symbols = []
        tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)

        
        for state, paths in self.transitions.items():
            for symbols in paths.keys():
                length = len(symbols)
        
        symbolsss = ()
        while length > 0:
            symbolsss +=self.left_end,
            length -= 1
        zoznam = self._length_transition(current_state, symbolsss)
        
        while zoznam and counter < 200:
            tape1 = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
            if len(zoznam) > 1 and cross == None and crossnumber == None :
                cross = len(str(zoznam[-1]))
                crossnumber = str(zoznam[-1])[-1]
            all_tapes = []
            all_tapes.append(tape1)
            tapes = []
            current_directions = []
            input_symbols = []

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

            count_x = 0
            counter +=1 
            zoznam1 = zoznam.pop(0)

            input_symbolss = ()
            input_symbolss += tape1.read_symbol(),
            for i in tapes:
                all_tapes.append(i)
                input_symbolss += i.read_symbol(),
            current_state = self.initial_state
            
            count = 0

            for possition in str(zoznam1):
                count_x = 0
                poss = possition
                count += 1
                if count == len(str(zoznam1)):
                    try:
                        (current),a,b = self._get_transition(current_state, input_symbolss,poss)
                        current_state = current[count_x]
                        count_x +=1
                        if current_state in self.final_states:
                            return zoznam1, cycle, cross, crossnumber
                        new_tape_symbol = current[count_x]
                        count_x +=1
                        tape1.write_symbol(new_tape_symbol)
                        for i in tapes:
                            new_tape_symbol = current[count_x]
                            count_x += 1
                            i.write_symbol(new_tape_symbol)

                        current_direction = current[count_x]
                        count_x +=1
                        tape1.move(current_direction)
                        for i in tapes:
                            current_direction = current[count_x]
                            count_x +=1
                            i.move(current_direction)


                        input_symbolss = ()
                        input_symbolss += tape1.read_symbol(),
                        for i in tapes:
                            all_tapes.append(i)
                            input_symbolss += i.read_symbol(),
                        
                        z = self._length_transition(current_state, input_symbolss)
                        if z and current_state != self.reject_state:
                            for i in z:
                                zoznam.append(int(str(zoznam1)+str(i)))
                    except ValueError:
                        (a) = self._get_transition(current_state, input_symbolss,poss)
                else:
                    (current),a,b = self._get_transition(current_state, input_symbolss,poss)
                    current_state = current[count_x]
                    count_x +=1
                    new_tape_symbol = current[count_x]
                    count_x +=1
                    tape1.write_symbol(new_tape_symbol)
                    for i in tapes:
                        new_tape_symbol = current[count_x]
                        count_x += 1
                        i.write_symbol(new_tape_symbol)

                    current_direction = current[count_x]
                    count_x +=1
                    tape1.move(current_direction)
                    for i in tapes:
                        current_direction = current[count_x]
                        count_x +=1
                        i.move(current_direction)
                        
                    input_symbolss = ()
                    input_symbolss += tape1.read_symbol(),
                    for i in tapes:
                        all_tapes.append(i)
                        input_symbolss += i.read_symbol(),
        else:          
            current_state = self.initial_state
            symbolsss = ()
            while length > 0:
                symbolsss +=self.left_end,
                length -= 1

            zz = self._length_transition(current_state, symbolsss)
            tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
        
            while True and counter1 < 200:
                counter1 +=1
                possition = 1
                if len(zz) > 1:
                    possition = random.randrange(1,len(zz)+1)
                z1+=str(possition)
                all_tapes = []
                all_tapes.append(tape1)
                tapes = []
                current_directions = []
                input_symbols = []
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
                count_x = 0

                input_symbolss = ()
                input_symbolss += tape.read_symbol(),
                for i in tapes:
                    all_tapes.append(i)
                    input_symbolss += i.read_symbol(),
                try:
                    (current),a,b = self._get_transition(current_state, input_symbolss,possition)    
                    current_state = current[count_x]
                    count_x +=1
                    new_tape_symbol = current[count_x]
                    count_x +=1
                    tape.write_symbol(new_tape_symbol)
                    for i in tapes:
                        new_tape_symbol = current[count_x]
                        count_x += 1
                        i.write_symbol(new_tape_symbol)
                    current_direction = current[count_x]
                    count_x +=1
                    tape.move(current_direction)
                    for i in tapes:
                        current_direction = current[count_x]
                        count_x +=1
                        i.move(current_direction)

                    input_symbolss = ()
                    input_symbolss += tape1.read_symbol(),
                    for i in tapes:
                        all_tapes.append(i)
                        input_symbolss += i.read_symbol(),


                    zz = self._length_transition(current_state, input_symbolss)
                    if current_state == self.reject_state:
                        return z1, cycle, cross, crossnumber
                except ValueError:
                    (current) = self._get_transition(current_state, input_symbolss,possition)
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
        tapes = []
        current_directions = []
        input_symbols = []

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
        for i in str(final):
            all_tapes = []
            all_tapes.append(tape)
            count_x = 0
                   
            input_symbolss = ()
            input_symbolss += tape.read_symbol(),
            for t in tapes:
                all_tapes.append(t)
                input_symbolss += t.read_symbol(),
                    
            try:
                (current),state1,current_state1 = self._get_transition1(current_state, input_symbolss,i)
            except ValueError:
                current_state,state = self._get_transition1(current_state, input_symbolss,i)
                current = ()
                current += current_state,
                for s in state:
                    current +=s,
                for t in tapes:
                    current += None,
                current += None,
                yield None,None,None, state,current_state ,all_tapes, current, final, cycle, cross, crossnumber
                break
        
            current_state = current[count_x]
            count_x += 1
            new_tape_symbol = current[count_x]
            count_x += 1

            for t in tapes:
                new_tape_symbol = current[count_x]
                count_x +=1
                t.write_symbol(new_tape_symbol)
                
            current_direction = current[count_x]
            count_x +=1
            tape.move(current_direction)
            for t in tapes:
                current_direction = current[count_x]
                count_x +=1
                t.move(current_direction)
            yield current_state, new_tape_symbol, current_direction,state1,current_state1,all_tapes,current,final, cycle, cross, crossnumber
            
                       
        input_symbolss = ()
        input_symbolss += tape.read_symbol(),
        current = ()
        current += current_state,
        current += tape.read_symbol(),
        for t in tapes:
            input_symbolss += t.read_symbol(),
            current += t.read_symbol(),
        for t in tapes:
            current += None,
        current += None,
        if current_state in self.final_states:
            yield None,None,None,input_symbolss,current_state, all_tapes, current, final, cycle, cross, crossnumber
        elif current_state in self.reject_state:
            yield None,None,None,input_symbolss,current_state, all_tapes, current, final, cycle, cross, crossnumber
        elif cycle == True:
            yield None,None,None,input_symbolss,current_state, all_tapes, current, final, cycle, cross, crossnumber
     
        
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
        tapes = []
        current_directions = []
        input_symbols = []

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
        for i in str(final):
            all_tapes = []
            all_tapes.append(tape)
            count_x = 0

            input_symbolss = ()
            input_symbolss += tape.read_symbol(),
            for t in tapes:
                all_tapes.append(t)
                input_symbolss += t.read_symbol(),
                
            z = self._length_transition(current_state, input_symbolss)
            if z:
                crossnumber.append(str(z[-1])[-1])
            try:
                (current),state1,current_state1 = self._get_transition1(current_state, input_symbolss,i)
            except ValueError:
                current_state,state  = self._get_transition1(current_state, input_symbolss,i)
                cycle1 = False
                current = ()
                current += current_state,
                for s in state:
                    current +=s,
                for t in tapes:
                    current += None,
                current += None,
                yield None,None,None, state, current_state,all_tapes,current , cycle,crossnumber
                break
            
            current_state = current[count_x]
            count_x += 1
            new_tape_symbol = current[count_x]
            count_x += 1
            
            for t in tapes:
                new_tape_symbol = current[count_x]
                count_x +=1
                t.write_symbol(new_tape_symbol)
                
            current_direction = current[count_x]
            count_x +=1
            tape.move(current_direction)
            for t in tapes:
                current_direction = current[count_x]
                count_x +=1
                t.move(current_direction)
            yield current_state, new_tape_symbol, current_direction,state1,current_state1,all_tapes,current, cycle, crossnumber


        input_symbolss = ()
        input_symbolss += tape.read_symbol(),
        current = ()
        current += current_state,
        current += tape.read_symbol(),
        for t in tapes:
            input_symbolss += t.read_symbol(),
            current += t.read_symbol(),
        for t in tapes:
            current += None,
        current += None,

            
        crossnumber.append('1')
        if current_state in self.final_states:
            cycle1 = False
            yield None,None,None,input_symbolss,current_state, all_tapes,current ,cycle, crossnumber
        elif current_state in self.reject_state:
            cycle1 = False
            yield None,None,None,input_symbolss,current_state, all_tapes, current, cycle, crossnumber
        elif cycle1:
            yield None,None,None,input_symbolss,current_state, all_tapes, current, cycle1, crossnumber

        
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

        tapes = []
        current_directions = []
        input_symbols = []
 
        for state, paths in self.transitions.items():
            for symbols in paths.keys():
                length = len(symbols)
        
        symbolsss = ()
        while length > 0:
            symbolsss +=self.left_end,
            length -= 1
        zoznam = self._length_transition(current_state, symbolsss)
        
        while zoznam and counter < 200:
            if len(zoznam) > 1 and cross == None and crossnumber == None :
                cross = len(str(zoznam[-1]))
                crossnumber = str(zoznam[-1])[-1]
            counter +=1 
            zoznam1 = zoznam.pop(0)

            tape_n = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
            all_tapes = []
            all_tapes.append(tape_n)
            current_directions = []
            input_symbols = []
            current_state = self.initial_state

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
                
            count_x = 0


            input_symbolss = ()
            input_symbolss += tape_n.read_symbol(),
            for i in tapes:
                all_tapes.append(i)
                input_symbolss += i.read_symbol(),
            current_state = self.initial_state

            
            count = 0
            for possition in str(zoznam1):
                count_x = 0
                poss = possition
                count += 1
                if count == len(str(zoznam1)):
                    try:
                        (current),a,b = self._get_transition(current_state, input_symbolss,poss)
                        current_state = current[count_x]
                        count_x +=1
                        if current_state in self.final_states:
                            return zoznam1, cycle, cross, crossnumber
                        new_tape_symbol = current[count_x]
                        count_x +=1
                        tape_n.write_symbol(new_tape_symbol)
                        for i in tapes:
                            new_tape_symbol = current[count_x]
                            count_x += 1
                            i.write_symbol(new_tape_symbol)
                        current_direction = current[count_x]
                        count_x +=1
                        tape_n.move(current_direction)
                        for i in tapes:
                            current_direction = current[count_x]
                            count_x +=1
                            i.move(current_direction)
                        
                        input_symbolss = ()
                        input_symbolss += tape_n.read_symbol(),
                        for i in tapes:
                            all_tapes.append(i)
                            input_symbolss += i.read_symbol(),
                            
                        z = self._length_transition(current_state, input_symbolss)
                        if z and current_state != self.reject_state:
                            for i in z:
                                zoznam.append(int(str(zoznam1)+str(i)))
                    except ValueError:
                        (a) = self._get_transition(current_state, input_symbolss,poss)
                else:
                    (current),a,b = self._get_transition(current_state, input_symbolss,poss)
                    current_state = current[count_x]
                    count_x +=1
                    new_tape_symbol = current[count_x]
                    count_x +=1
                    tape_n.write_symbol(new_tape_symbol)
                    for i in tapes:
                        new_tape_symbol = current[count_x]
                        count_x += 1
                        i.write_symbol(new_tape_symbol)

                    current_direction = current[count_x]
                    count_x +=1
                    tape_n.move(current_direction)
                    for i in tapes:
                        current_direction = current[count_x]
                        count_x +=1
                        i.move(current_direction)
                        
                    input_symbolss = ()
                    input_symbolss += tape_n.read_symbol(),
                    for i in tapes:
                        all_tapes.append(i)
                        input_symbolss += i.read_symbol(),
                         
        else:
            tape = TMTape(self.left_end+input_str, blank_symbol=self.blank_symbol)
            current_direction = None
            current_state = self.initial_state
            symbolsss = ()
            while length > 0:
                symbolsss +=self.left_end,
                length -= 1
                
            for i in str(none_zoznam):
                all_tapes = []
                all_tapes.append(tape)
                tapes = []
                current_directions = []
                input_symbols = []
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
                count_x = 0

                try:
                    (current),a,b = self._get_transition1(current_state, input_symbolsss,i)
                except ValueError:
                    state,current_state = self._get_transition1(current_state, input_symbolsss,i)
                    break
                for i in tapes:
                    new_tape_symbol = current[count_x]
                    count_x += 1
                    i.write_symbol(new_tape_symbol)
                current_direction = current[count_x]
                count_x +=1
                tape.move(current_direction)
                for i in tapes:
                    current_direction = current[count_x]
                    count_x +=1
                    i.move(current_direction)
                    

            symbolsss = ()
            while length > 0:
                symbolsss +=self.left_end,
                length -= 1

            zz = self._length_transition(current_state, input_symbolsss)
            while True and counter1 < 200:
                counter1 +=1
                possition = 1
                if len(zz) > 1:
                    possition = random.randrange(1,len(zz)+1)
                z1+=str(possition)
                
                all_tapes = []
                all_tapes.append(tape1)
                tapes = []
                current_directions = []
                input_symbols = []
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
                count_x = 0

                input_symbolss = ()
                input_symbolss += tape.read_symbol(),
                for i in tapes:
                    all_tapes.append(i)
                    input_symbolss += i.read_symbol(),
                try:
                    (current),a,b = self._get_transition(current_state, input_symbolss,possition)    
                    current_state = current[count_x]
                    count_x +=1
                    new_tape_symbol = current[count_x]
                    count_x +=1
                    tape.write_symbol(new_tape_symbol)
                    for i in tapes:
                        new_tape_symbol = current[count_x]
                        count_x += 1
                        i.write_symbol(new_tape_symbol)
                    current_direction = current[count_x]
                    count_x +=1
                    tape.move(current_direction)
                    for i in tapes:
                        current_direction = current[count_x]
                        count_x +=1
                        i.move(current_direction)

                    input_symbolss = ()
                    input_symbolss += tape1.read_symbol(),
                    for i in tapes:
                        all_tapes.append(i)
                        input_symbolss += i.read_symbol(),

                    
                    input_symbolss = ()
                    input_symbolss += tape1.read_symbol(),
                    for i in tapes:
                        all_tapes.append(i)
                        input_symbolss += i.read_symbol(),
                        
                    zz = self._length_transition(current_state, input_symbolss)
                    if current_state == self.reject_state:
                        return z1, cycle, cross, crossnumber
                except ValueError:
                    (current) = self._get_transition(current_state, input_symbol,possition)
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
        tapes = []
        current_directions = []
        input_symbols = []
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
            
        for i in str(final):
            all_tapes = []
            all_tapes.append(tape)
            count_x = 0

            input_symbolss = ()
            input_symbolss += tape.read_symbol(),
            for t in tapes:
                all_tapes.append(t)
                input_symbolss += t.read_symbol(),
                
            try:
                (current),state1,current_state1 = self._get_transition1(current_state, input_symbolss,i)

            except ValueError:
                current_state,state = self._get_transition1(current_state, input_symbolss,i)
                current = ()
                current += current_state,
                for s in state:
                    current +=s,
                for t in tapes:
                    current += None,
                current += None,
                yield None,None,None, state,current_state ,all_tapes, current, final, cycle, cross, crossnumber
                break

            current_state = current[count_x]
            count_x += 1
            new_tape_symbol = current[count_x]
            count_x += 1
            
            for t in tapes:
                new_tape_symbol = current[count_x]
                count_x +=1
                t.write_symbol(new_tape_symbol)
                
            current_direction = current[count_x]
            count_x +=1
            tape.move(current_direction)
            for t in tapes:
                current_direction = current[count_x]
                count_x +=1
                t.move(current_direction)
            yield current_state, new_tape_symbol, current_direction,state1,current_state1, all_tapes,current, final, cycle, cross, crossnumber



        input_symbolss = ()
        input_symbolss += tape.read_symbol(),
        current = ()
        current += current_state,
        current += tape.read_symbol(),
        for t in tapes:
            input_symbolss += t.read_symbol(),
            current += t.read_symbol(),
        for t in tapes:
            current += None,
        current += None,
        
        if current_state in self.final_states:
            yield None,None,None,input_symbolss,current_state, all_tapes, current, final, cycle, cross, crossnumber
        elif current_state in self.reject_state:
            yield None,None,None,input_symbolss,current_state, all_tapes, current, final, cycle, cross, crossnumber
        elif cycle == True:
            yield None,None,None,input_symbolss,current_state, all_tapes, current, final, cycle, cross, crossnumber
  
