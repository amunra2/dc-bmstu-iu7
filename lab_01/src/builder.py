import copy
from automata import NFA, DFA, EPSILON
from typing import Dict, List, Tuple


def merge_tables(A, B):
    keys = set(list(A.table.keys()) + list(B.table.keys()))
    new_final = [state + A.num_of_states() for state in B.final_states]
    new_final.extend(A.final_states)
    new_table = {}
    for k in keys:
        new_row = []
        if k in A.table:
            new_row.extend(A.table[k])
        else:
            new_row.extend([[] for _ in range(A.num_of_states())])
        if k in B.table:
            new_row.extend([[s + A.num_of_states() for s in states] for states in B.table[k]])
        else:
            new_row.extend([[] for _ in range(B.num_of_states())])
        new_table[k] = new_row
    return NFA(table=new_table, final_states=new_final)


def concatenate(A, B):
    merged = merge_tables(A, B)
    for start in A.final_states:
        merged.add_transition(start, EPSILON, A.num_of_states())
    merged.final_states = [s + A.num_of_states() for s in B.final_states]
    return merged


def alternate(A, B):
    merged = merge_tables(A, B)
    shifted_finals = [f + 1 for f in merged.final_states]
    shifted_table = {}
    for char, state_list in merged.table.items():
        shifted_table[char] = [[]] + [[state + 1 for state in states] for states in state_list] + [[]]
    new = NFA(table=shifted_table, final_states=[])
    new.add_transition(0, EPSILON, 1)
    new.add_transition(0, EPSILON, A.num_of_states() + 1)
    for f in shifted_finals:
        new.add_transition(f, EPSILON, new.num_of_states() - 1)
    new.final_states = [new.num_of_states() - 1]
    return new


def star(A):
    shifted_finals = [f + 1 for f in A.final_states]
    shifted_table = {}
    for char, state_list in A.table.items():
        shifted_table[char] = [[]] + [[state + 1 for state in states] for states in state_list] + [[]]
    new = NFA(table=shifted_table, final_states=[])
    for f in shifted_finals:
        new.add_transition(f, EPSILON, 1)
        new.add_transition(f, EPSILON, new.num_of_states() - 1)
    new.add_transition(0, EPSILON, 1)
    new.add_transition(0, EPSILON, new.num_of_states() - 1)
    new.final_states = [new.num_of_states() - 1]
    return new


def plus(A):
    return concatenate(A, star(A))


def primitive_nfda(actual_string):
    table: Dict[str, List[List[int]]] = {}
    for i, c in enumerate(actual_string):
        if c not in table:
            table[c] = [[] for _ in range(len(actual_string) + 1)]
        table[c][i].append(i + 1)
    return NFA(table=table, final_states=[len(actual_string)])


operations = {
    '*': star,
    '+': plus,
    '|': alternate,
    ',': concatenate
}
priorities = {
    '|': 0,
    ',': 1,
    '*': 2,
    '+': 2
}

binary = ['|', ',']
unary = ['*', '+', '?']


def is_character(c):
    return c not in (list(operations.keys()) + ['(', ')'])


def prepare_regexp(regexp):
    if len(regexp) == 0:
        return ''
    new = []
    last = None
    for c in regexp:
        if last is None:
            last = c
            new.append(c)
            continue
        if last in unary and c == '(' \
            or last in unary and is_character(c) \
            or is_character(last) and is_character(c) \
            or last == ')' and is_character(c) \
            or is_character(last) and c == '(':
            new.append(',')
        new.append(c)
        last = c
    return ''.join(new)


def create_nfa(regexp):
    if not regexp:
        raise ValueError("Error: Empty regexp")

    op_stack = []
    automata_stack = []
    buffer = ''

    def avalanche(priority=-1):
        while len(op_stack) != 0 \
                and op_stack[-1] != '(' \
                and (op_stack[-1] not in operations.keys() or priorities[op_stack[-1]] > priority):
            op = op_stack[-1]
            if op in binary:
                automata_stack.append(operations[op](automata_stack[-2], automata_stack[-1]))
                automata_stack.pop(-2)
                automata_stack.pop(-2)
                op_stack.pop()
            elif op in unary:
                automata_stack.append(operations[op](automata_stack[-1]))
                automata_stack.pop(-2)
                op_stack.pop()
        if priority == -1 and len(op_stack) != 0 and op_stack[-1] == '(':
            op_stack.pop()

    regexp = prepare_regexp(regexp)

    for c in regexp:
        if c in list(operations.keys()) + ['(', ')']:
            if buffer != '':
                automata_stack.append(primitive_nfda(buffer))
            buffer = ''
        if c in operations:
            if len(op_stack) == 0 or op_stack[-1] in ['(', ')'] or priorities[op_stack[-1]] < priorities[c]:
                op_stack.append(c)
            else:
                avalanche(priorities[c])
                op_stack.append(c)
        elif c == '(':
            op_stack.append('(')
        elif c == ')':
            avalanche()
        else:
            buffer += c

    if buffer != '':
        automata_stack.append(primitive_nfda(buffer))
    avalanche()
    
    return automata_stack[-1]


def convert_to_dfa(nfda):
    links = []
    newStates = [set(nfda.eps_close(0))]
    visitedStates = []
    alphabet = [x for x in list(nfda.table.keys()) if x != EPSILON]
    while len(newStates) > 0:
        tmp = newStates.pop()
        if tmp in visitedStates:
            continue
        visitedStates.append(tmp)
        for char in alphabet:
            newTmp = set(nfda.forward(tmp, char))
            if len(newTmp) != 0:
                newStates.append(newTmp)
                links.append((tmp, char, newTmp))
    formatted_links = []
    for link in links:
        formatted_links.append((visitedStates.index(link[0]), link[1], visitedStates.index(link[2])))
    links = formatted_links
    old_final = set(nfda.final_states)
    new_final = [i for i, s in enumerate(visitedStates) if s.intersection(old_final)]
    new_table = {}
    for k in alphabet:
        new_table[k] = [None for _ in enumerate(visitedStates)]
    for link in links:
        new_table[link[1]][link[0]] = link[2]
    return DFA(table=new_table, final_states=new_final)



def min_brzhzovskiy(fda: DFA):
    fda.revertDFA()
    fda.detDFA()
    fda.revertDFA()
    fda.detDFA()
    return fda


def minimize_fda(dfa: DFA):
    dfa = min_brzhzovskiy(dfa)
    return DFA(table=dfa.table, final_states=dfa.final_states)




# class DfaStandart: # ранее рассмотренное представление не подходит для использования алгоритма Бржозовского
#     def __init__(self) -> None:
#         self.Q = [] # состояния
#         self.A = [] # алфавит
#         self.T = [] # функции переходов -> состояние: в какие переходит и по какой букве
#         self.S = [] # начальные состояния
#         self.F = [] # конечные состояния

#     def convertFromDFA(self, dfa: DFA) -> None:
#         if dfa.table:
#             self.A = dfa.alphabet()
#             self.F = dfa.final_states

#             num_of_states = dfa.num_of_states()
#             self.Q = [i for i in range(num_of_states)]

#             self.S = self.__getStartStatesFromDFA(dfa, self.Q[:])
#             self.T = copy.deepcopy(dfa.proxy.table)

#     def revertDFA(self) -> None:
#         final_state_tmp = self.F[:]
#         self.F = self.S
#         self.S = final_state_tmp

#         new_table = {char: [[] for _ in range(len(self.Q))] for char in self.A}

#         for char, state_list in self.T.items():
#             for start_state, char_states in enumerate(state_list):
#                 if len(char_states) != 0:
#                     for end_state in char_states:
#                         new_table[char][end_state].append(start_state)

#         self.T = new_table

#     def detDFA(self) -> None:
#         def reachable(q, state):
#             t = dict()
#             for char in self.A:
#                 ts = set()
#                 for i in q[state]:
#                     ts |= set(self.T[char][i])
#                 if not ts:
#                     t[char] = []
#                     continue
#                 try:
#                     i = q.index(ts)
#                 except ValueError:
#                     i = len(q)
#                     q.append(ts)
#                 t[char] = [i]
#             return t

#         q = [set(self.S)]
#         new_table = {char: [] for char in self.A}

#         while len(list(new_table.values())[0]) < len(q):
#             tmp = reachable(q, len(list(new_table.values())[0])) # -> {a: [[]], b: [[]]}
#             for char in self.A:
#                 new_table[char].append(tmp[char])
        
#         self.S = [0]
#         self.Q = [i for i in range(0, len(q))]
#         self.F = [q.index(i) for i in q if set(self.F) & i]
#         self.T = new_table


#     def __getStartStatesFromDFA(self, dfa: DFA, Q: List[int]) -> List[int]:
#         for _, state_list in dfa.proxy.table.items():
#             for start_state, char_states in enumerate(state_list):
#                 if len(char_states) != 0:
#                     for end_state in char_states:
#                         if start_state != end_state and end_state in Q:
#                             Q.remove(end_state)
#         return Q
