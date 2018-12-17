#!/usr/bin/env python3
"""Classes and methods for working with all Turing machines."""

import abc

from turing_machine import exceptions
from turing_machine.automaton import Automaton


class TM(Automaton, metaclass=abc.ABCMeta):
    """An abstract base class for Turing machines."""

    def _validate_input_symbol_subset(self):
        if not (self.input_symbols < self.tape_symbols):
            raise exceptions.MissingSymbolError(
                'V množine páskových symbolov chýbajú symboly z  '
                'množiny vstupných symbolov ({})'.format(
                    self.tape_symbols - self.input_symbols))
    
    def _validate_nonfinal_initial_state(self):
        """Raise an error if the initial state is a final state."""
        if self.initial_state in self.final_states:
            raise exceptions.InitialStateError(
                'Počiatocný stav  {} nemôže byť akceptujúci stav'.format(
                    self.initial_state))
