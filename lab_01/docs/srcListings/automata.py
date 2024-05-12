import os
os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

from graphviz import Digraph
from typing import Dict, List, Set
import copy
import numpy as np

FDA_table = Dict[str, List[int]]
NFDA_table = Dict[str, List[List[int]]]
EPSILON = 'e'


class CharCantBeAccepted(Exception):
    pass


class Automata:
    def accepts(self, input_string):
        raise NotImplementedError()

    def num_of_states(self):
        raise NotImplementedError()

    def getAlphabet(self):
        raise NotImplementedError()
    
    def show_automata(self):
        raise NotImplementedError()


class NFA(Automata):
    def __init__(self, table: NFDA_table, final_states):
        self.table = table
        self.final_states = final_states

        self.states = None

    def next_state(self, state, char):
        if char not in self.table:
            raise CharCantBeAccepted
        return self.table[char][state]

    def forward(self, old_state, char):
        new_state = set()
        for state in old_state:
            new_state.update(self.next_state(state, char))
            if EPSILON in self.table.keys():
                new_state.update(sum([self.eps_close(s) for s in new_state], []))
        return list(new_state)

    def add_transition(self, start, char, finish):
        if char not in self.table:
            self.table[char] = [[] for _ in range(self.num_of_states())]
        self.table[char][start].append(finish)

    def accepts(self, input_string):
        self.states = self.eps_close(0)
        try:
            for c in input_string:
                self.states = self.forward(self.states, c)
            for state in self.states:
                if set(self.eps_close(state)).intersection(self.final_states):
                    return True
            return False
        except CharCantBeAccepted:
            return False

    def num_of_states(self):
        return len(list(self.table.values())[0])

    def copy(self):
        new_table = copy.deepcopy(self.table)
        new_final = copy.deepcopy(self.final_states)
        return NFA(new_table, new_final)

    def show_automata(self, type):
        dot = Digraph()
        
        for char, state_list in self.table.items():
            for i, s in enumerate(state_list):
                if len(s) != 0:
                    for t in s:
                        dot.edge(str(i), str(t), char)

        for i in self.final_states:
            dot.node(str(i),shape='cds')
        
        dot.edge('START', '0')
        
        if type == 1:
            dot.render('НКА', view=True)
        if type == 2:
            dot.render('ДКА', view=True)
        if type == 3:
            dot.render('МДКА', view=True)


    def eps_close(self, state: int) -> List[int]:
        if EPSILON not in self.table.keys():
            return [state]
        visited = []
        active = [state]
        while len(active) != 0:
            new_active = []
            for s in active:
                new_active.extend(self.table[EPSILON][s])
            visited = list(set(visited + active))
            active = list(set(new_active).difference(visited))
        return visited

    def getAlphabet(self):
        return list(self.table.keys())

class DFA(Automata):
    def __init__(self, table: FDA_table, final_states: List[int]):
        # Q = states
        # A = alhabet
        # T = table
        # S = start_states
        # F = final_state
        self.table = table
        self.final_states = final_states
        self.proxy = NFA(self.__getNFATableFromDFATable(), final_states)

        num_of_states = self.num_of_states()
        self.states = [i for i in range(num_of_states)]
        self.start_states = self.__getStartStates(self.states[:])
        self.alphabet = self.getAlphabet()
    
    def __getNFATableFromDFATable(self):
        proxy_table = {}

        for char, states in self.table.items():
            proxy_table[char] = [[state] if state is not None else [] for state in states]

        return proxy_table
    
    def __getDFATableFromNFATable(self):
        table = {char:[] for char in self.alphabet}
        isStop = False

        for char, states in self.proxy.table.items():
            if isStop:
                break

            for state in states:
                statesNum = len(state)
                if statesNum == 0:
                    table[char].append(None)
                elif statesNum == 1:
                    table[char].append(state[0])
                else:
                    # print("ERROR: __getDFATableFromNFATable:", self.proxy.table)
                    table = {}
                    isStop = not isStop
                    break

        return table

    def accepts(self, input_string: str) -> bool:
        return self.proxy.accepts(input_string)

    def show_automata(self, type):
        self.proxy.show_automata(type)

    def num_of_states(self):
        return self.proxy.num_of_states()

    def getAlphabet(self):
        return self.proxy.getAlphabet()
    
    def revertDFA(self) -> None:
        final_state_tmp = self.final_states[:]
        self.final_states = self.start_states
        self.start_states = final_state_tmp

        new_table = {char: [[] for _ in range(len(self.states))] for char in self.alphabet}

        for char, state_list in self.proxy.table.items():
            for start_state, char_states in enumerate(state_list):
                if len(char_states) != 0:
                    for end_state in char_states:
                        new_table[char][end_state].append(start_state)

        self.proxy.table = new_table
        self.table = self.__getDFATableFromNFATable()

    def detDFA(self) -> None:
        def reachable(q, state):
            t = dict()
            for char in self.alphabet:
                ts = set()
                for i in q[state]:
                    ts |= set(self.proxy.table[char][i])
                if not ts:
                    t[char] = []
                    continue
                try:
                    i = q.index(ts)
                except ValueError:
                    i = len(q)
                    q.append(ts)
                t[char] = [i]
            return t

        q = [set(self.start_states)]
        new_table = {char: [] for char in self.alphabet}

        while len(list(new_table.values())[0]) < len(q):
            tmp = reachable(q, len(list(new_table.values())[0])) # -> {a: [[]], b: [[]]}
            for char in self.alphabet:
                new_table[char].append(tmp[char])
        
        self.start_states = [0]
        self.states = [i for i in range(0, len(q))]
        self.final_states = [q.index(i) for i in q if set(self.final_states) & i]
        self.proxy.table = new_table
        self.table = self.__getDFATableFromNFATable()
    
    def model_check(self, check_str):
        check_arr = [*check_str]
        size = len(self.table[list(self.table.keys())[0]])
        Ssize = len(self.table)
        true_table = np.full((size,size,Ssize), None)
        j = 0
        for char, state_list in self.table.items():
            for i, s in enumerate(state_list):
                if s != None:
                    true_table[i][s][j] = char
            j += 1
        
        carette = 0
        
        while(True):
            if not check_arr:
                break
            for i in range(size):
                if check_arr:
                    arr = []
                    for a in true_table[carette]:
                        for b in a:
                            arr.append(b)
                    if check_arr[0] not in arr:
                        print('ERROR')
                        return
                    for symbol in true_table[carette][i]:
                        if check_arr[0] == symbol:
                            check_arr.pop(0)
                            carette = i
                            break

        if not check_arr and carette in self.final_states:
            print('OK')
        else:
            print('ERROR')

        return
    
    def __getStartStates(self, states: List[int]) -> List[int]:
        for _, state_list in self.proxy.table.items():
            for start_state, char_states in enumerate(state_list):
                if len(char_states) != 0:
                    for end_state in char_states:
                        if start_state != end_state and end_state in states:
                            states.remove(end_state)
        return states