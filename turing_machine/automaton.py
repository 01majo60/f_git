#!/usr/bin/env python3
"""Turing machines."""

import abc

from turing_machine import exceptions



class Automaton(metaclass=abc.ABCMeta):
    """An abstract base class for all Turing machines."""

    @abc.abstractmethod
    def __init__(self, obj=None, **kwargs):
        """Initialize a complete tm."""
        pass

    @abc.abstractmethod
    def validate_self(self):
        """Return True if this tm is internally consistent."""
        pass

    @abc.abstractmethod
    def _validate_input_yield(self, input_str):
        """Check if the given string is accepted by this tm."""
        pass

    def _validate_input_return(self, input_str):
        """
        Check if the given string is accepted by this tm.

        Return the tm's final configuration if this string is valid.
        """
        validation_generator = self._validate_input_yield(input_str)
        for config in validation_generator:
            pass
        return config


    def validate_input_ntm_final(self, input_str,final ,step = False):
        """
        Check if the given string is accepted by this tm.

        If step is True, yield the configuration at each step.
        """
        if step:
            return self._validate_input_yield_final(input_str,final)
        else:
            pass

    def validate_input_ntm_none_final(self, input_str,final ,step = False):
        """
        Check if the given string is accepted by this tm.

        If step is True, yield the configuration at each step.
        """
        if step:
            return self._validate_input_yield_none_final(input_str,final)
        else:
            pass
        

    def validate_input(self, input_str, step=False):
        """
        Check if the given string is accepted by this tm.

        If step is True, yield the configuration at each step. Otherwise,
        return the final configuration.
        """
        if step:
            return self._validate_input_yield(input_str)
        else:
            return self._validate_input_return(input_str)

    def validate_input1(self, input_str, step=False):
        """
        Check if the given string is accepted by this tm.

        If step is True, yield the configuration at each step. Otherwise,
        return the final configuration.
        """
        if step:
            return self._validate_input_yield1(input_str)
        else:
            return self._validate_input_return1(input_str)
        
    def _validate_input_return1(self, input_str):
        """
        Check if the given string is accepted by this tm.

        Return the tm's final configuration if this string is valid.
        """
        validation_generator = self._validate_input_yield1(input_str)
        for config in validation_generator:
            pass
        return config

    def _validate_initial_state(self):
        """Raise an error if the initial state is invalid."""
        if self.initial_state not in self.states:
            raise exceptions.InvalidStateError(
                '{} nie je platný počiatočný stav, nenachádza sa v množine stavov'.format(self.initial_state))

    def _validate_initial_state_transitions(self):
        """Raise an error if the initial state has no transitions defined."""
        if self.initial_state not in self.transitions:
            raise exceptions.MissingStateError(
                'Počiatočný stav {} nemá definovaný prechod v prechodovej funkcii'.format(
                    self.initial_state))

    def _validate_final_states(self):
        """Raise an error if any final states are invalid."""
        final = {self.final_states}
        invalid_states = final - self.states
        if invalid_states:
            raise exceptions.InvalidStateError(
                'Akceptujúci stav ({}) nie je platný, nenachádza sa v množine stavov'.format(
                    ', '.join(invalid_states)))
        
    def _validate_reject_state(self):
        """Raise an error if reject state are invalid."""
        reject = {self.reject_state}
        invalid_states = reject - self.states
        if invalid_states:
            raise exceptions.InvalidStateError(
                'Zamietajúci stav ({}) nie je platný, nenachádza sa v množine stavov'.format(
                    ', '.join(invalid_states)))

    def copy(self):
        """Create a deep copy of the tm."""
        return self.__class__(self)

    def __eq__(self, other):
        """Check if two tm are equal."""
        return self.__dict__ == other.__dict__
