from pythonds.basic.stack import Stack


ALPHABET = "qwertyuiopasdfghjklzxcvbnm0123456789"


def convertRegexToDesiredFormat(regex: str) -> str | None:
    regex = regex.replace(" ", "").lower()
    try:
        checkRegex(regex)
    except ValueError as exc:
        print(f"\n{exc}\n")
        return None

    regex = convertToDesiredFormat(regex)
    # print(f"\nОбработанное регулярное выражение:\n{regex}\n")

    return regex


def checkRegex(regex: str) -> None:
    alphabet = ALPHABET + "()*|"
    for symbol in regex:
        if symbol not in alphabet:
            raise ValueError(f"Недопустимый символ для регулярного выражения '{symbol}'")

    openBracketsCount = 0
    stack = Stack()
    lettersBetween = 0
    for symbol in regex:
        if symbol == '(':
            openBracketsCount += 1
            stack.push(lettersBetween + 1)
            lettersBetween = 0
        elif symbol == ')':
            if openBracketsCount > 0:
                openBracketsCount -= 1
            else:
                raise ValueError("Неверная постановка скобок в регулярном выражении")
            
            # в скобках должно быть хотя бы одно выражение
            if lettersBetween < 2:
                raise ValueError("Неверная постановка скобок в регулярном выражении")
            else:
                lettersBetween = stack.pop()
        elif symbol != '|':
            lettersBetween += 1

    if openBracketsCount > 0:
        raise ValueError("Не все скобки в регулярном выражении были закрыты")

    lenRegex = len(regex)
    for i in range(lenRegex):
        if regex[i] == '|' and (
            i == 0 or \
            i == lenRegex - 1 or \
            regex[i - 1] in ['|', '('] or \
            regex[i + 1] in ['|', '*', ')'] 
        ):
            raise ValueError("Недопустимое расположение символа '|'")
        
        if regex[i] == '*' and (
            i == 0 or \
            regex[i - 1] in ['|', '*', '(']
        ):
            raise ValueError("Недопустимое расположение символа '*'")


def convertToDesiredFormat(regex: str):
    resRegex = ""
    lenRegex = len(regex)
    for i in range(lenRegex):
        resRegex += regex[i]
        if regex[i] in ALPHABET + "*)" and \
            i != lenRegex - 1 and \
            regex[i + 1] not in ['|', '*', ')']:
            resRegex += '.'

    # учет приоритета оператора '*'
    i = 1
    while i < len(resRegex):
        if resRegex[i] == "*":
            if resRegex[i - 1] != ")":
                resRegex = f"{resRegex[:i - 1]}({resRegex[i - 1:i + 1]}){resRegex[i + 1:]}"
            else:
                openingBracketIndex = findOpeningBracketIndex(resRegex, i - 1)
                resRegex = f"{resRegex[:openingBracketIndex]}({resRegex[openingBracketIndex:i + 1]}){resRegex[i + 1:]}"
            i += 2
        i += 1

    return resRegex + ".#"


def findOpeningBracketIndex(regex: str, closingBracketIndex: int) -> int:
    regex = regex[:closingBracketIndex][::-1]
    closingBracketsCount = 0
    openingBracketIndex = 0
    for i in range(len(regex)):
        if regex[i] == ')':
            closingBracketsCount += 1
        elif regex[i] == '(':
            if closingBracketsCount > 0:
                closingBracketsCount -= 1
            else:
                openingBracketIndex = i
                break

    return closingBracketIndex - openingBracketIndex - 1


def findClosingBracketIndex(regex: str, openingBracketIndex: int) -> int:
    regex = regex[openingBracketIndex + 1:]
    openBracketsCount = 0
    closingBracketIndex = 0
    for i in range(len(regex)):
        if regex[i] == '(':
            openBracketsCount += 1
        elif regex[i] == ')':
            if openBracketsCount > 0:
                openBracketsCount -= 1
            else:
                closingBracketIndex = i
                break

    return openingBracketIndex + closingBracketIndex + 1
