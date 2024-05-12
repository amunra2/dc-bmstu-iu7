from builder import *
import sys


def main():
    regexp = input("Введите регулярное выражение: ")
    # regexp = "a(ab*)*"
    # regexp = "(ab*)+ab"

    nfa = create_nfa(regexp)
    nfa.show_automata(1)

    dfa = convert_to_dfa(nfa)
    dfa.show_automata(2)

    mdfa = minimize_fda(dfa)
    mdfa.show_automata(3)

    while(True):
        check = input("Введите строку для моделирования МКА (для выхода введите 'N'): ")
        if check.upper() == 'N':
            exit()
        else:
            mdfa.model_check(check)

if __name__ == "__main__":
    main()
