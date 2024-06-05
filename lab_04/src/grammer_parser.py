from graphviz import Digraph
from typing import Tuple, List


PRINT_EPS_NODES = False

pos = 0


class Node:
  def __init__(self, value):
    self.value = value
    self.children = []
    self.res = []

  def print(self, tree=None, parent_value="", id="main"):
    if not tree:
      tree = Digraph()
      tree.node_attr["shape"] = "plain"

    if not PRINT_EPS_NODES and self._is_empty_node():
      return tree

    if self.value == '<>':
      tree.node(id, str('\<\>') + '\n' + " ".join(self.res))
    else:
      tree.node(id, str(self.value) + '\n' + " ".join(self.res))

    if parent_value:
      tree.edge(parent_value, id)

    for i, child in enumerate(self.children):
      child.print(tree, id, id + "." + str(i))

    return tree
  
  def _is_empty_node(self):
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
    new_node.res = [lexemes[pos]]
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
    new_node.res = [lexemes[pos]]
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
    new_node.res = [lexemes[pos]]
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
    new_node.res = [lexemes[pos]]
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
    new_node.res = [lexemes[pos]]
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
  new_node.res = [lexemes[pos]]
  tree.children.append(new_node)
  pos += 1

  return True


def parse_factor(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<фактор\>")
  if parse_identifier(new_node, lexemes) or parse_const(new_node, lexemes):
    new_node.res = new_node.children[0].res
    tree.children.append(new_node)
    return True
  
  elif parse_lex(new_node, lexemes, '('):
    if parse_simple_expr(new_node, lexemes):
      if parse_lex(new_node, lexemes, ')'):
        new_node.res = new_node.children[1].res
        tree.children.append(new_node)
        return True
      
  elif parse_lex(new_node, lexemes, 'not'):
    if parse_factor(new_node, lexemes):
      new_node.res = new_node.children[1].res + ['not']
      tree.children.append(new_node)
      return True

  return False


def parse_therm_stroke(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<терм’\>")
  if parse_mult_oper_type(new_node, lexemes):
    if parse_factor(new_node, lexemes):
      if parse_therm_stroke(new_node, lexemes):
        new_node.res = \
          new_node.children[1].res + \
          new_node.children[0].res + \
          new_node.children[2].res
        
        tree.children.append(new_node)
        return True
      
    return False

  new_node.children.append(Node("ε"))
  tree.children.append(new_node)

  return True


def parse_therm(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<терм\>")
  if parse_factor(new_node, lexemes):
    if parse_therm_stroke(new_node, lexemes):
      for c in new_node.children:
        new_node.res += c.res

      tree.children.append(new_node)
      return True

  return False


def parse_simple_expr_stroke(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<простое выражение’\>")
  if parse_addition_oper_type(new_node, lexemes):
    if parse_therm(new_node, lexemes):
      if parse_simple_expr_stroke(new_node, lexemes):
        new_node.res = \
          new_node.children[1].res + \
          new_node.children[0].res + \
          new_node.children[2].res
        
        tree.children.append(new_node)
        return True
      
    return False

  new_node.children.append(Node("ε"))
  tree.children.append(new_node)

  return True


def parse_simple_expr(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<простое выражение\>")
  if parse_therm(new_node, lexemes):
    if parse_simple_expr_stroke(new_node, lexemes):
      new_node.res = \
        new_node.children[0].res + \
        new_node.children[1].res
      
      tree.children.append(new_node)
      return True
    
  elif parse_sign(new_node, lexemes):
    if parse_therm(new_node, lexemes):
      if parse_simple_expr_stroke(new_node, lexemes):
        new_node.res = ['0'] + \
          new_node.children[1].res + \
          new_node.children[0].res + \
          new_node.children[2].res
        
        tree.children.append(new_node)
        return True

  return False


def parse_expr(tree: Node, lexemes: List[str]) -> bool:
  new_node = Node("\<выражение\>")
  if parse_simple_expr(new_node, lexemes):
    if parse_relation_oper(new_node, lexemes):
      if parse_simple_expr(new_node, lexemes):
        new_node.res = \
          new_node.children[0].res + \
          new_node.children[2].res + \
          new_node.children[1].res
        
        tree.children.append(new_node)
        return True
      else:
        return False

    new_node.res = new_node.children[0].res
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
    elif string[curr_pos: min(curr_pos + 3, len(string))] in ['not', 'div', 'mod', 'and', 'end']:
      tokens += [string[curr_pos: min(curr_pos + 3, len(string))]]
      curr_pos += 3
    elif string[curr_pos: min(curr_pos + 2, len(string))] in ['or', '<>', '<=', '>=', ':=']:
      tokens += [string[curr_pos: min(curr_pos + 2, len(string))]]
      curr_pos += 2
    elif string[curr_pos] in ['=', '<', '>', '+', '-', '*', '/', '(', ')', ';']:
      tokens += [string[curr_pos]]
      curr_pos += 1
    elif string[curr_pos] in [' ', '\t', '\n', '\r']:
      curr_pos += 1
    else:
      start_pos = curr_pos
      while curr_pos < len(string) and (string[curr_pos].isalpha() or string[curr_pos].isnumeric() or string[curr_pos] in ["_", '.']):
        curr_pos += 1

      tokens += [string[start_pos: curr_pos]]
      if start_pos == curr_pos:
        print("ERROR")
        break

  return tokens


def parse(test: List[Tuple[str]], view=True):
  lexems = tokenize(test[0])
  print(lexems)

  global pos
  pos = 0
  tree = Node("head")
  res = parse_expr(tree, lexems)

  if not res or pos != len(lexems):
    print("Syntax error!")
    return

  tree.children[0].print().render("../docs/tree", view=view)

  print("Выражение в обратной польской нотации:")
  res = " ".join(tree.children[0].res)
  print(res)

  if res == test[1]:
    print("Верно")
  else:
    print("Ошибка")
