
from graphviz import Digraph
from typing import List

PARSE_PROGRAM = "parse_program"
PRINT_EPS_NODES = True

pos = 0


class Node:
  def __init__(self, data):
    self.value = data
    self.children = []

  def print(self, tree=None, parent_value="", id="main"):
    if not tree:
      tree = Digraph()
      tree.node_attr["shape"] = "plain"

    if not PRINT_EPS_NODES and self._is_empty_node():
      return tree

    if self.value == '<>':
      tree.node(id, str('\<\>'))
    else:
      tree.node(id, str(self.value))

    if parent_value:
      tree.edge(parent_value, id)

    for i, child in enumerate(self.children):
      child.print(tree, id, id + "." + str(i))

    return tree
  
  def _is_empty_node(self) -> bool:
    if len(self.children) == 1 and self.children[0].value == 'ε':
      return True
    
    return False


def parse_mult_oper_type(tree: Node, lexemes: List[str]) -> bool:
  global pos
  if pos >= len(lexemes):
    return False

  if lexemes[pos] in ['*', '/', 'div', 'mod', 'and']:
    new_node = Node('\<операция типа умножения\>')
    new_node.children.append(Node(lexemes[pos]))
    tree.children.append(new_node)
    pos += 1
    return True
  
  return False


def parse_addition_oper_type(tree: Node, lexemes: List[str]) -> bool:
  global pos
  if pos >= len(lexemes):
    return False

  if lexemes[pos] in ['+', '-', 'or']:
    new_node = Node("\<операция типа сложения\>")
    new_node.children.append(Node(lexemes[pos]))
    tree.children.append(new_node)
    pos += 1
    return True
  
  return False


def parse_sign(tree: Node, lexemes: List[str]) -> bool:
  global pos
  if pos >= len(lexemes):
    return False

  if lexemes[pos] in ['+', '-']:
    new_node = Node("\<знак\>")
    new_node.children.append(Node(lexemes[pos]))
    tree.children.append(new_node)
    pos += 1
    return True
  
  return False


def parse_relation_oper(tree: Node, lexemes: List[str]) -> bool:
  global pos
  if pos >= len(lexemes):
    return False

  if lexemes[pos] in ['=', '<>', '<', '<=', '>', '>=']:
    new_node = Node("\<операция отношения\>")
    new_node.children.append(Node(lexemes[pos]))
    tree.children.append(new_node)
    pos += 1
    return True
  
  return False


def parse_identifier(tree: Node, lexemes: List[str]) -> bool:
  global pos
  if pos >= len(lexemes):
    return False

  if lexemes[pos].isalpha() and lexemes[pos] not in ['begin', 'end', 'div', 'mod', 'and', 'or', 'not']:
    new_node = Node("\<идентификатор\>")
    new_node.children.append(Node(lexemes[pos]))
    tree.children.append(new_node)
    pos += 1
    return True
  
  return False


def parse_const(tree: Node, lexemes: List[str]) -> bool:
  global pos
  if pos >= len(lexemes):
    return False

  try:
    value = int(lexemes[pos])
  except:
    try:
      value = float(lexemes[pos])
    except:
      return False

  new_node = Node("\<константа\>")
  new_node.children.append(Node(value))
  tree.children.append(new_node)
  pos += 1

  return True


def parse_factor(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<фактор\>")
  if parse_identifier(new_node, lexemes) \
    or parse_const(new_node, lexemes):

    tree.children.append(new_node)
    return True

  elif parse_lex(new_node, lexemes, '(') \
    and parse_simple_expr(new_node, lexemes) \
    and parse_lex(new_node, lexemes, ')'):

    tree.children.append(new_node)
    return True
      
  elif parse_lex(new_node, lexemes, 'not') \
    and parse_factor(new_node, lexemes):

    tree.children.append(new_node)
    return True

  return False


def parse_therm_stroke(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<терм’\>")
  if parse_mult_oper_type(new_node, lexemes):
    if parse_factor(new_node, lexemes) \
      and parse_therm_stroke(new_node, lexemes):
      
      tree.children.append(new_node)
      return True
    else:
      return False

  new_node.children.append(Node("ε"))
  tree.children.append(new_node)

  return True


def parse_therm(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<терм\>")
  if parse_factor(new_node, lexemes) \
    and parse_therm_stroke(new_node, lexemes):

    tree.children.append(new_node)
    return True

  return False


def parse_simple_expr_stroke(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<простое выражение’\>")
  if parse_addition_oper_type(new_node, lexemes):
    if parse_therm(new_node, lexemes) \
      and parse_simple_expr_stroke(new_node, lexemes):

      tree.children.append(new_node)
      return True
    else:
      return False

  new_node.children.append(Node("ε"))
  tree.children.append(new_node)

  return True


def parse_simple_expr(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<простое выражение\>")
  if parse_therm(new_node, lexemes) \
    and parse_simple_expr_stroke(new_node, lexemes):
    
    tree.children.append(new_node)
    return True
    
  elif parse_sign(new_node, lexemes) \
    and parse_therm(new_node, lexemes) \
    and parse_simple_expr_stroke(new_node, lexemes):

    tree.children.append(new_node)
    return True

  return False


def parse_expr(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<выражение\>")
  if parse_simple_expr(new_node, lexemes):
    if parse_relation_oper(new_node, lexemes):
      if parse_simple_expr(new_node, lexemes):
        tree.children.append(new_node)
        return True
      else:
        return False

    tree.children.append(new_node)
    return True

  return False


def parse_operator(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<оператор\>")
  if parse_identifier(new_node, lexemes) and \
    parse_lex(new_node, lexemes, ':=') and \
    parse_expr(new_node, lexemes):

    tree.children.append(new_node)
    return True

  return False


def parse_operator_list_stroke(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<список операторов’\>")
  if parse_lex(new_node, lexemes, ';'):
    if parse_operator(new_node, lexemes) \
      and parse_operator_list_stroke(new_node, lexemes):

      tree.children.append(new_node)
      return True
    else:
      return False

  new_node.children.append(Node("ε"))
  tree.children.append(new_node)
  
  return True


def parse_operator_list(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<список операторов\>")
  if parse_operator(new_node, lexemes) \
    and parse_operator_list_stroke(new_node, lexemes):

    tree.children.append(new_node)
    return True

  return False


def parse_block(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<блок\>")
  if parse_lex(new_node, lexemes, 'begin') \
    and parse_operator_list(new_node, lexemes) \
    and parse_lex(new_node, lexemes, 'end'):

    tree.children.append(new_node)
    return True
      
  return False


def parse_program(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<программа\>")
  if parse_block(new_node, lexemes):
    tree.children.append(new_node)
    return True

  return False


def parse_lex(tree: Node, lexemes: List[str], lex: str) -> bool:
  global pos
  if pos >= len(lexemes):
    return False

  if lexemes[pos] == lex:
    tree.children.append(Node(lex))
    pos += 1
    return True

  return False


def tokenize(string: str) -> List[str]:
  tokens = []
  curr_pos = 0
  while curr_pos < len(string):
    if string[curr_pos: min(curr_pos + 5, len(string))] in ['begin']:
      tokens += [string[curr_pos: min(curr_pos + 5, len(string))]]
      curr_pos += 5
    elif string[curr_pos : min(curr_pos + 3, len(string))] in ['not', 'div', 'mod', 'and', 'end']:
      tokens += [string[curr_pos: min(curr_pos + 3, len(string))]]
      curr_pos += 3
    elif string[curr_pos: min(curr_pos + 2, len(string))] in ['or', '<>', '<=', '>=', ':=']:
      tokens += [string[curr_pos: min(curr_pos + 2, len(string))]]
      curr_pos += 2
    elif string[curr_pos] in ['=', '<', '>', '+', '-', '*', '/', '(', ')', ';']:
      tokens += [string[curr_pos]]
      curr_pos += 1
    elif string[curr_pos] in ['\n', '\t', ' ', '\r']:
      curr_pos += 1
    else:
      start_pos = curr_pos
      while curr_pos < len(string) and \
        (string[curr_pos].isalpha() or string[curr_pos].isnumeric() or string[curr_pos] in ["_", '.']):
        curr_pos += 1

      if start_pos != curr_pos:
        tokens += [string[start_pos: curr_pos]]
      else:
        print("ERROR")
        break
      
  return tokens


def parse(lexems: List[str]) -> None:
  tree = Node("head")
  
  res = parse_program(tree, lexems)

  if not res or pos != len(lexems):
    print("Syntax error!")
    return

  tree.children[0].print().render("../docs/tree", view=True)
