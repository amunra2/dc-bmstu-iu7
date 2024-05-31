from functools import reduce
from copy import deepcopy


class Grammar:
  notTerminals: list[str]
  terminals: list[str]
  rules: dict[str, list[list[str]]]
  start: str
  
  def __init__(
    self, 
    notTerminals: list[str],
    terminals: list[str], 
    rules: dict[str, list[list[str]]], 
    start: str
  ) -> None:
    self.notTerminals = notTerminals
    self.terminals = terminals
    self.rules = rules
    self.start = start

  def printGrammar(self) -> None:
    notTerminals = Grammar.__joinListWithSymbol(self.notTerminals, ", ")
    terminals = Grammar.__joinListWithSymbol(self.terminals, ", ")

    print(f"\nG = ({{{notTerminals}}}, {{{terminals}}}, P, {self.start}), где P состоит из правил:\n")
    for  notTerminal in self.notTerminals:
      rightRules = self.rules[notTerminal]
      self.__printProduct(notTerminal, rightRules)

  def removeLeftRecursion(self) -> None:
    i = 0
    while i < len(self.notTerminals):
      copyRightRules = self.rules[self.notTerminals[i]].copy()
      for j in range(i):
        self.__replaceProducts(
          notTerminal=self.notTerminals[i],
          replaceableNotTerminal=self.notTerminals[j],
        )
      if self.__removeDirectLeftRecursion(self.notTerminals[i]):
        i += 2
      else:
        self.rules[self.notTerminals[i]] = copyRightRules
        i += 1
  
  def removeLeftFactorization(self) -> None:
    i = 0
    while i < len(self.notTerminals):
      maxPrefix = ""
      rightRules = self.rules[self.notTerminals[i]]
      for j in range(len(rightRules)):
        prefix = ""
        for symbol in rightRules[j]:
          indexList = self.__findPrefixMatches(
            rightRules=rightRules,
            prefix=prefix + symbol,
          )
          if len(indexList) > 1:
            prefix += symbol
          else:
            break
        
        if len(prefix) > len(maxPrefix):
          maxPrefix = prefix
      
      if maxPrefix:
        print(f"\nСамый длинный префикс для {self.notTerminals[i]}: {maxPrefix}")
        self.__removeDirectLeftFactorization(self.notTerminals[i], maxPrefix)
      else:
        i += 1

  def convertToChomskyForm(self) -> None:
    for notTerminal in self.notTerminals.copy():
      for i in range(len(self.rules[notTerminal])):
        rightRule = self.rules[notTerminal][i]
        if len(rightRule) == 2 and \
          rightRule[0] in self.notTerminals and \
          rightRule[1] in self.notTerminals or \
          len(rightRule) == 1 and rightRule[0] in self.terminals or \
          notTerminal == self.start and rightRule[0] == "e":
          continue
        
        elif len(rightRule) == 2 and \
          (rightRule[0] in self.terminals or rightRule[1] in self.terminals):
          if rightRule[0] in self.terminals:
            firstElem = f"{rightRule[0]}'"
            if not firstElem in self.notTerminals:
              self.notTerminals.append(firstElem)
              self.rules[firstElem] = [[rightRule[0]]]
          else:
            firstElem = rightRule[0]

          if rightRule[1] in self.terminals:
            secondElem = f"{rightRule[1]}'"
            if not secondElem in self.notTerminals:
              self.notTerminals.append(secondElem)
              self.rules[secondElem] = [[rightRule[1]]]
          else:
            secondElem = rightRule[1]

          self.rules[notTerminal][i] = [firstElem, secondElem]

        elif len(rightRule) > 2:
          if rightRule[0] in self.notTerminals:
            self.rules[notTerminal][i] = [rightRule[0], f"<{''.join(rightRule[1:])}>"]
          else:
            self.rules[notTerminal][i] = [f"{rightRule[0]}'", f"<{''.join(rightRule[1:])}>"]
            if not f"{rightRule[0]}'" in self.notTerminals:
              self.notTerminals.append(f"{rightRule[0]}'")
              self.rules[f"{rightRule[0]}'"] = [[rightRule[0]]]

          rightRule = rightRule[1:]
          newNotTerminal = f"<{''.join(rightRule)}>"
          while len(rightRule) > 2:
            if not newNotTerminal in self.notTerminals:
              self.notTerminals.append(newNotTerminal)
      
              if rightRule[0] in self.notTerminals:
                self.rules[newNotTerminal] = [[rightRule[0], f"<{''.join(rightRule[1:])}>"]]
              else:
                self.rules[newNotTerminal] = [[f"{rightRule[0]}'", f"<{''.join(rightRule[1:])}>"]]
                if not f"{rightRule[0]}'" in self.notTerminals:
                  self.notTerminals.append(f"{rightRule[0]}'")
                  self.rules[f"{rightRule[0]}'"] = [[rightRule[0]]]

            rightRule = rightRule[1:]
            newNotTerminal = f"<{''.join(rightRule)}>"

          newNotTerminal = f"<{''.join(rightRule)}>"
          if not newNotTerminal in self.notTerminals:
            if rightRule[0] in self.terminals:
              firstElem = f"{rightRule[0]}'"
              if not firstElem in self.notTerminals:
                self.notTerminals.append(firstElem)
                self.rules[firstElem] = [[rightRule[0]]]
            else:
              firstElem = rightRule[0]

            if rightRule[1] in self.terminals:
              secondElem = f"{rightRule[1]}'"
              if not secondElem in self.notTerminals:
                self.notTerminals.append(secondElem)
                self.rules[secondElem] = [[rightRule[1]]]
            else:
              secondElem = rightRule[1]
            
            self.notTerminals.append(newNotTerminal)
            self.rules[newNotTerminal] = [[firstElem, secondElem]]
             
  def createFileFromGrammar(self, fileName: str) -> None:
    with open(fileName, "w") as f:
      for i in range(len(self.notTerminals)):
        if i:
          f.write(" ")
        f.write(f"{self.notTerminals[i]}")
      f.write("\n")

      for i in range(len(self.terminals)):
        if i:
          f.write(" ")
        f.write(f"{self.terminals[i]}")
      f.write("\n")

      for notTerminal in self.notTerminals:
        for rightRule in self.rules[notTerminal]:
          f.write(f"{notTerminal} ->")
          for symbol in rightRule:
            f.write(f" {symbol}")
          f.write("\n")
      
      f.write(f"{self.start}\n")

  def __removeDirectLeftFactorization(self, notTerminal: str, maxPrefix: str) -> None:
    indexList = self.__findPrefixMatches(
      rightRules=self.rules[notTerminal],
      prefix=maxPrefix,
    )
    newRightRules = []
    lenMaxPrefix = len(maxPrefix)
    for i in indexList:
      if len(self.rules[notTerminal][i]) > lenMaxPrefix:
        newRightRules.append(self.rules[notTerminal][i][lenMaxPrefix:])
      else:
        newRightRules.append(["e"])

    rightRules = []
    for i in range(len(self.rules[notTerminal])):
      if not i in indexList:
        rightRules.append(self.rules[notTerminal][i])

    newNotTerminal = self.__findNewNotTerminal(notTerminal)
    self.rules[newNotTerminal] = newRightRules
    self.rules[notTerminal] = \
      [list(maxPrefix) + [newNotTerminal]] + rightRules
    
    indexNotTerminal = self.notTerminals.index(notTerminal)
    self.notTerminals = \
      self.notTerminals[:indexNotTerminal + 1] + [newNotTerminal] + \
      self.notTerminals[indexNotTerminal + 1:]
    
  def __findNewNotTerminal(self, notTerminal: str):
    try:
      baseNotTerminal = notTerminal[:notTerminal.index("'")]
    except ValueError:
      baseNotTerminal = notTerminal

    quotationMarkCount = 0
    for item in self.notTerminals:
      if item.find(baseNotTerminal) != -1:
        quotationMarkCount += 1
    
    return notTerminal + "'" * quotationMarkCount

  def __findPrefixMatches(self, rightRules: list[list[str]], prefix: str) -> list[int]:
    indexList = []
    for i in range(len(rightRules)):
      if self.__comparePrefixes(rightRules[i], prefix):
        indexList.append(i)
    
    return indexList
  
  def __comparePrefixes(self, rightRule: list[str], prefix: str) -> bool:
    if len(rightRule) < len(prefix):
      return False

    for i in range(len(prefix)):
      if prefix[i] != rightRule[i]:
        return False
      
    return True

  def __replaceProducts(self, notTerminal: str, replaceableNotTerminal: str) -> None:
    flagReplace = False
    newRightRules = []
    rightRules = self.rules[notTerminal]
    for i in range(len(rightRules)):
      if replaceableNotTerminal not in rightRules[i]:
        newRightRules.append(rightRules[i])
        continue
      
      flagReplace = True
      j = rightRules[i].index(replaceableNotTerminal)
      for substitutedRightRule in self.rules[replaceableNotTerminal]:
        newRightRule = rightRules[i][:j]
        if substitutedRightRule[0] != "e":
          newRightRule.extend(substitutedRightRule)
        newRightRule.extend(rightRules[i][j + 1:])
        newRightRules.append(newRightRule)
    
    if flagReplace:
      self.rules[notTerminal] = newRightRules
      print(f"\nПосле замены {replaceableNotTerminal}: ", end="")
      self.__printProduct(notTerminal, newRightRules)

  def __removeDirectLeftRecursion(self, notTerminal: str) -> bool:
    self.rules[notTerminal].sort(
      key=lambda rightRule: rightRule[0] != notTerminal
    )
    newNotTerminal = notTerminal + "'"
    rightRulesForNewNotTerminal = []
    rightRules = []

    for rightRule in deepcopy(self.rules[notTerminal]):
      if rightRule[0] != notTerminal:
        if rightRule[0] == "e":
          rightRule = [newNotTerminal]
        else:
          rightRule.append(newNotTerminal)
        rightRules.append(rightRule)
      else:
        rightRule = rightRule[1:]
        rightRule.append(newNotTerminal)
        rightRulesForNewNotTerminal.append(rightRule)

    if len(rightRulesForNewNotTerminal):
      rightRulesForNewNotTerminal.append(["e"])
      indexNotTerminal = self.notTerminals.index(notTerminal)
      self.notTerminals = \
        self.notTerminals[:indexNotTerminal + 1] + [newNotTerminal] + \
        self.notTerminals[indexNotTerminal + 1:]
      self.rules[newNotTerminal] = rightRulesForNewNotTerminal
      self.rules[notTerminal] = rightRules

      removedFlag = True
    else:
      removedFlag = False

    return removedFlag
  
  def __printProduct(self, notTerminal: str, rightRules: list[list[str]]):
    print(f"{notTerminal} -> ", end="")
    for i in range(len(rightRules)):
      print(f"{' | ' if i != 0 else ''}{Grammar.__joinListWithSymbol(rightRules[i], ' ')}", end="")
    print()

  @staticmethod
  def __joinListWithSymbol(arr: list[str], symbol: str) -> str:
    return reduce(lambda elemPrev, elem: f"{elemPrev}{symbol}{elem}", arr)


def reedGrammarFromFile(fileName: str) -> Grammar:
  with open(fileName) as f:
    lines = [line[:-1] for line in f.readlines()]

  notTerminals = lines[0].split(" ")
  terminals = lines[1].split(" ")
  start = lines[-1]
  rules = {}
  for notTerminal in notTerminals:
    rules[notTerminal] = []

  for rule in lines[2:-1]:
    rule = rule.split(" ")
    rules[rule[0]].append(rule[2:])

  return Grammar(
    notTerminals=notTerminals, 
    terminals=terminals,
    rules=rules,
    start=start,
  )
