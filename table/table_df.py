from turing_machine.dtm import DTM
from turing_machine.ntm import NTM
from turing_machine.xdtm import XDTM
from turing_machine.xntm import XNTM
import pandas as pd
from importlib import import_module
from ast import literal_eval
from app.models import Tmachine

def table(name,druh):
    input_s = "{"
    if druh == "dtm":
        df, input_symbols = dtm_table(name)
    elif druh == "ntm":
        df, input_symbols = ntm_table(name)
    elif druh == "xtm":
        df, input_symbols = xtm_table(name)
    elif druh == 'xntm':
        df, input_symbols = xntm_table(name)
    for i in input_symbols:
        input_s += i + ", "
    input_s = input_s[:-2]
    input_s +="}"
    return df, input_s, input_symbols

    
def dtm_table(name):
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
        
        
    dtm = DTM(
        states = literal_eval(states_d),
        input_symbols= literal_eval(input_symbols_d),
        tape_symbols= literal_eval(tape_symbols_d),
        left_end = left_end_d,
        transitions=literal_eval(transitions_d),
        initial_state= initial_state_d,
        blank_symbol= blank_symbol_d,
        reject_state= reject_state_d,
        final_states= final_states_d
    )
    
    dc = dtm.transitions
    df = pd.DataFrame.from_dict(data=dc,orient='index')
    df.fillna("( -, -, - )",inplace=True)
    rows, columns = df.shape

    z1=[]
    z2=[]
    for i in dtm.tape_symbols:
         z2.append("( -, -, - )")
         z1.append("( -, -, - )")
    df1 = pd.DataFrame([z1], index = [dtm.final_states], columns=list(df.columns.values))
    df2 = pd.DataFrame([z2], index = [dtm.reject_state], columns=list(df.columns.values))
    df = df.append(df1)
    df = df.append(df2)

    return df, dtm.input_symbols     

def change_ntm(x):
    word1 = ""
    if x == "( -, -, - )":
        return x
    else:
        counter = 1
        for i in x:
            word = ', '.join(i)
            if counter == len(x):
                word1 += '(' +word+')'
            else:
                word1 += '(' +word+'), '
            counter +=1
        return word1

def ntm_table(name):
    
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
        
    ntm = NTM(
        states = literal_eval(states_d),
        input_symbols= literal_eval(input_symbols_d),
        tape_symbols= literal_eval(tape_symbols_d),
        left_end = left_end_d,
        transitions=literal_eval(transitions_d),
        initial_state= initial_state_d,
        blank_symbol= blank_symbol_d,
        reject_state= reject_state_d,
        final_states= final_states_d
    )   

    dc = ntm.transitions
    df = pd.DataFrame.from_dict(data=dc,orient='index')   
    df.fillna("( -, -, - )",inplace=True)
    df = df.applymap(lambda x: change_ntm(x))
    rows, columns = df.shape
    z1=[]
    z2=[]
    for i in ntm.tape_symbols:
         z2.append("( -, -, - )")
         z1.append("( -, -, - )")
    df1 = pd.DataFrame([z1], index = [ntm.final_states], columns=list(df.columns.values))
    df2 = pd.DataFrame([z2], index = [ntm.reject_state], columns=list(df.columns.values))
    df = df.append(df1)
    df = df.append(df2)

    return df, ntm.input_symbols  

def xtm_table(name):
    
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
        
    xdtm = XDTM(
        states = literal_eval(states_d),
        input_symbols= literal_eval(input_symbols_d),
        tape_symbols= literal_eval(tape_symbols_d),
        left_end = left_end_d,
        transitions=literal_eval(transitions_d),
        initial_state= initial_state_d,
        blank_symbol= blank_symbol_d,
        reject_state= reject_state_d,
        final_states= final_states_d
    )

    dc = xdtm.transitions
    first = dc.keys()
    second = []
    for i in first:
        for j in dc[i].keys():
            second.append(j)
    list(set(second))
    
    df = pd.DataFrame(data=dc,index=second)
    df = df.T
    
    df.fillna("( -, -, - )",inplace=True)
    rows, columns = df.shape
    z1=[]
    z2=[]
    for i in range(columns):
         z2.append("( -, -, - )")
         z1.append("( -, -, - )")
    df1 = pd.DataFrame([z1], index = [xdtm.final_states], columns=list(df.columns.values))
    df2 = pd.DataFrame([z2], index = [xdtm.reject_state], columns=list(df.columns.values))
    df = df.append(df1)
    df = df.append(df2)

    return df, xdtm.input_symbols

def xntm_table(name):
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
        
    xntm = XNTM(
        states = literal_eval(states_d),
        input_symbols= literal_eval(input_symbols_d),
        tape_symbols= literal_eval(tape_symbols_d),
        left_end = left_end_d,
        transitions=literal_eval(transitions_d),
        initial_state= initial_state_d,
        blank_symbol= blank_symbol_d,
        reject_state= reject_state_d,
        final_states= final_states_d
    )   
    
    dc = xntm.transitions
    first = dc.keys()
    second = []
    for i in first:
        for j in dc[i].keys():
            second.append(j)
    list(set(second))
    
    df = pd.DataFrame(data=dc,index=second)
    df = df.T

    df.fillna("( -, -, - )",inplace=True)
    df = df.applymap(lambda x: change_ntm(x))
    
    rows, columns = df.shape
    z1=[]
    z2=[]
    for i in range(columns):
        z2.append("( -, -, - )")
        z1.append("( -, -, - )")

    df1 = pd.DataFrame([z1], index = [xntm.final_states], columns=list(df.columns.values))
    df2 = pd.DataFrame([z2], index = [xntm.reject_state], columns=list(df.columns.values))
    df = df.append(df1)
    df = df.append(df2)

    return df, xntm.input_symbols     




