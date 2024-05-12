import unittest

from builder import *


class TestDFA:
  def __init__(self,
      states: List[int],
      alphabet: List[str],
      table,
      start_states: List[int],
      final_states: List[int],
  ):
    self.states = states
    self.alphabet = alphabet
    self.table = table
    self.start_states = start_states
    self.final_states = final_states


class TestDFAMethod(unittest.TestCase):
  def test_oneChar(self):
    dfa: DFA = self.__getDFA("a")

    test_dfa = TestDFA(
      states=[0,1],
      alphabet=["a"],
      table={"a": [1, None]},
      start_states=[0],
      final_states=[1],
    )

    self.__assert(dfa, test_dfa)


  def test_oneCharPlus(self):
    dfa: DFA = self.__getDFA("a+")

    test_dfa = TestDFA(
      states=[0,1],
      alphabet=["a"],
      table={"a": [1, 1]},
      start_states=[0],
      final_states=[1],
    )

    self.__assert(dfa, test_dfa)

  def test_oneCharStar(self):
    dfa: DFA = self.__getDFA("a*")

    test_dfa = TestDFA(
      states=[0],
      alphabet=["a"],
      table={"a": [0]},
      start_states=[0],
      final_states=[0],
    )

    self.__assert(dfa, test_dfa)

  def test_twoChars(self):
    dfa: DFA = self.__getDFA("ab")

    test_dfa = TestDFA(
      states=[0,1,2],
      alphabet=["a","b"],
      table={"a": [1,None,None], "b": [None,2,None]},
      start_states=[0],
      final_states=[2],
    )

    self.__assert(dfa, test_dfa)

  def test_twoCharsComplicated(self):
    dfa: DFA = self.__getDFA("(ab*)+ab")

    test_dfa = TestDFA(
      states=[0,1,2,3],
      alphabet=["a","b"],
      table={"a": [1,2,2,2], "b": [None,1,3,1]},
      start_states=[0],
      final_states=[3],
    )

    self.__assert(dfa, test_dfa)

  def test_empty(self):
    self.assertRaises(
      ValueError,
      create_nfa, ""
    )

  def __getDFA(self, regexp: str) -> DFA:
    nfa = create_nfa(regexp)
    dfa = convert_to_dfa(nfa)
    return minimize_fda(dfa)
  
  def __assert(self, dfa: DFA, test_dfa: TestDFA) -> None:
    self.assertEqual(dfa.states, test_dfa.states)
    self.assertEqual(dfa.alphabet.sort(), test_dfa.alphabet.sort())
    self.assertEqual(dfa.table, test_dfa.table)
    self.assertEqual(dfa.start_states, test_dfa.start_states)
    self.assertEqual(dfa.final_states, test_dfa.final_states)

if __name__ == "__main__":
  unittest.main()
