from flask import Flask, flash, session
from app import db
from app.main.forms import MyForm
from app.models import Tmachine
from ast import literal_eval
from flask_sqlalchemy import SQLAlchemy
from turing_machine.dtm import DTM
from turing_machine.ntm import NTM
from turing_machine.xdtm import XDTM
from turing_machine.xntm import XNTM
from turing_machine import exceptions
from sqlalchemy import exc

def upload(file):
    try:
        name = (file.readline()[:-2:]).decode("utf-8")
        druh = (file.readline()[:-2:]).decode("utf-8")
        states_u = (file.readline()[:-3:]).decode("utf-8")
        input_symbols_u = (file.readline()[:-3:]).decode("utf-8")
        tape_symbols_u = (file.readline()[:-3:]).decode("utf-8")
        left_end_u = (file.readline()[:-3:]).decode("utf-8")
        transitions_u = (file.readline()[:-3:]).decode("utf-8")
        initial_state_u = (file.readline()[:-3:]).decode("utf-8")
        blank_symbol_u = (file.readline()[:-3:]).decode("utf-8")
        reject_state_u = (file.readline()[:-3:]).decode("utf-8")
        final_states_u = (file.readline()[:-2:]).decode("utf-8")
    except:
        success_message = ('Súbor nebolo možné načítať')
        druh = False
        return success_message, druh
        
    
    if druh == 'DTM':
        form = MyForm()
        druh = 'dtm'
        tm = False
        try:
            dtm = DTM(
            states = literal_eval(states_u),
            input_symbols = literal_eval(input_symbols_u),
            tape_symbols= literal_eval(tape_symbols_u),
            left_end = literal_eval(left_end_u),
            transitions = literal_eval(transitions_u),
            initial_state = literal_eval(initial_state_u),
            blank_symbol = literal_eval(blank_symbol_u),
            reject_state = literal_eval(reject_state_u),
            final_states = literal_eval(final_states_u)
            )
            if dtm:
                tm = True
        except(exceptions.InvalidStateError,exceptions.InvalidSymbolError,exceptions.MissingStateError,exceptions.MissingSymbolError,
              exceptions.InitialStateError,exceptions.FinalStateError,exceptions.RejectStateError,exceptions.LeftEndError,
              exceptions.RejectionError,exceptions.InvalidDirectionError) as err:
            tm = False
            success_message = (err)
            return success_message, druh
        if tm:
            try:
                tmachine = Tmachine(definicia = name ,tm_d_n_x='dtm',
                                    states = states_u ,input_symbols = input_symbols_u,
                                    tape_symbols = tape_symbols_u ,left_end = literal_eval(left_end_u),
                                    transitions = transitions_u,
                                    initial_state = literal_eval(initial_state_u),
                                    blank_symbol = literal_eval(blank_symbol_u),reject_state = literal_eval(reject_state_u),
                                    final_states = literal_eval(final_states_u))
                
                db.session.add(tmachine)
                db.session.commit()
                success_message = True
                return success_message, druh
            except exc.IntegrityError:
                db.session().rollback()
                tm = False
                success_message = ("Názov turingovho stroja už existuje prosím zvolte iný názov")
                return success_message, druh
            
    elif druh == 'NTM':
        form = MyForm()
        druh = 'ntm'
        tm = False
        try:
            ntm = NTM(
            states = literal_eval(states_u),
            input_symbols= literal_eval(input_symbols_u),
            tape_symbols= literal_eval(tape_symbols_u),
            left_end = literal_eval(left_end_u),
            transitions = literal_eval(transitions_u),
            initial_state = literal_eval(initial_state_u),
            blank_symbol = literal_eval(blank_symbol_u),
            reject_state = literal_eval(reject_state_u),
            final_states = literal_eval(final_states_u)
            )
            if ntm:
                tm = True
        except(exceptions.InvalidStateError,exceptions.InvalidSymbolError,exceptions.MissingStateError,exceptions.MissingSymbolError,
              exceptions.InitialStateError,exceptions.FinalStateError,exceptions.RejectStateError,exceptions.LeftEndError,
              exceptions.RejectionError,exceptions.InvalidDirectionError) as err:
            tm = False
            success_message = (err)
            return success_message
        if tm:
            try:
                tmachine = Tmachine(definicia = name ,tm_d_n_x='ntm',
                                    states = states_u ,input_symbols = input_symbols_u,
                                    tape_symbols = tape_symbols_u ,left_end = literal_eval(left_end_u),
                                    transitions = transitions_u,
                                    initial_state = literal_eval(initial_state_u),
                                    blank_symbol = literal_eval(blank_symbol_u),reject_state = literal_eval(reject_state_u),
                                    final_states = literal_eval(final_states_u))
                
                db.session.add(tmachine)
                db.session.commit()
                success_message = True
                return success_message, druh
            except exc.IntegrityError:
                db.session().rollback()
                tm = False
                success_message = ("Názov turingovho stroja už existuje prosím zvolte iný názov")
                return success_message, druh

        
    elif druh == 'XDTM':
        form = MyForm()
        druh = 'xdtm'
        tm = False
        try:
            xdtm = XDTM(
            states = literal_eval(states_u),
            input_symbols= literal_eval(input_symbols_u),
            tape_symbols= literal_eval(tape_symbols_u),
            left_end = literal_eval(left_end_u),
            transitions = literal_eval(transitions_u),
            initial_state = literal_eval(initial_state_u),
            blank_symbol = literal_eval(blank_symbol_u),
            reject_state = literal_eval(reject_state_u),
            final_states = literal_eval(final_states_u)
            )
            if xdtm:
                tm = True
        except(exceptions.InvalidStateError,exceptions.InvalidSymbolError,exceptions.MissingStateError,exceptions.MissingSymbolError,
              exceptions.InitialStateError,exceptions.FinalStateError,exceptions.RejectStateError,exceptions.LeftEndError,
              exceptions.RejectionError,exceptions.InvalidDirectionError) as err:
            tm = False
            success_message = (err)
            return success_message
        if tm:
            try:
                tmachine = Tmachine(definicia = name ,tm_d_n_x='xtm',
                                    states = states_u ,input_symbols = input_symbols_u,
                                    tape_symbols = tape_symbols_u ,left_end = literal_eval(left_end_u),
                                    transitions = transitions_u,
                                    initial_state = literal_eval(initial_state_u),
                                    blank_symbol = literal_eval(blank_symbol_u),reject_state = literal_eval(reject_state_u),
                                    final_states = literal_eval(final_states_u))
                
                db.session.add(tmachine)
                db.session.commit()
                success_message = True
                return success_message, druh
            except exc.IntegrityError:
                db.session().rollback()
                tm = False
                success_message = ("Názov turingovho stroja už existuje prosím zvolte iný názov")
                return success_message, druh


    elif druh == 'XNTM':
        form = MyForm()
        druh = 'xntm'
        tm = False
        try:
            xntm = XNTM(
            states = literal_eval(states_u),
            input_symbols = literal_eval(input_symbols_u),
            tape_symbols= literal_eval(tape_symbols_u),
            left_end = literal_eval(left_end_u),
            transitions = literal_eval(transitions_u),
            initial_state = literal_eval(initial_state_u),
            blank_symbol = literal_eval(blank_symbol_u),
            reject_state = literal_eval(reject_state_u),
            final_states = literal_eval(final_states_u)
            )
            if xntm:
                tm = True
        except(exceptions.InvalidStateError,exceptions.InvalidSymbolError,exceptions.MissingStateError,exceptions.MissingSymbolError,
              exceptions.InitialStateError,exceptions.FinalStateError,exceptions.RejectStateError,exceptions.LeftEndError,
              exceptions.RejectionError,exceptions.InvalidDirectionError) as err:
            tm = False
            success_message = (err)
            return success_message, druh
        if tm:
            try:
                tmachine = Tmachine(definicia = name ,tm_d_n_x='xntm',
                                    states = states_u ,input_symbols = input_symbols_u,
                                    tape_symbols = tape_symbols_u ,left_end = literal_eval(left_end_u),
                                    transitions = transitions_u,
                                    initial_state = literal_eval(initial_state_u),
                                    blank_symbol = literal_eval(blank_symbol_u),reject_state = literal_eval(reject_state_u),
                                    final_states = literal_eval(final_states_u))
                
                db.session.add(tmachine)
                db.session.commit()
                success_message = True
                return success_message, druh
            except exc.IntegrityError:
                db.session().rollback()
                tm = False
                success_message = ("Názov turingovho stroja už existuje prosím zvolte iný názov")
                return success_message, druh
    else:
        success_message = "Turingov stroj nebolo možné načítať"
        druh = False
        return success_message, druh
