import subprocess

from grammar import Grammar, reedGrammarFromFile


SIZE_MENU = 5
OUTPUT_FILE_NAME = "./data/result.txt"
MENU = f"""
  \tМеню\n
  1.  Вывести исходную грамматику
  2.  Грамматика после устранения левой рекурсии
  3.  Грамматика после устранения левой факторизации
  4.  Грамматика после устранения левой рекурсии и левой факторизации
  5.  Преобразование КС-грамматики к нормальной форме Хомского

  0.  Выход\n
  Выбор: """


def inputOption(minOptions: int, maxOptions: int, msg: str):
  try:
    option = int(input(msg))
  except:
    option = -1
  else:
    if option < minOptions or option > maxOptions:
      option = -1
  
  if option == -1:
    print(f"\nОжидался ввод целого числа от {minOptions} до {maxOptions}")

  return option


def chooseInputFile() -> str:
  with open("temp.txt", "w") as f:
    subprocess.run(["ls", "./data"], stdout=f)

  with open("temp.txt") as f:
    fileNames = [line[:-1] for line in f.readlines()]

  subprocess.run(["rm", "temp.txt"])

  msg = f"\n\tВходные файлы:\n\n"
  for i in range(len(fileNames)):
    msg += f"  {i + 1}.  {fileNames[i]};\n"
  msg += f"\n  Выбор: "

  option = -1
  while option == -1:
    option = option = inputOption(
      minOptions=1,
      maxOptions=len(fileNames), 
      msg=msg,
    )
  
  return f"./data/{fileNames[option - 1]}"


def main():
  inputFile = chooseInputFile()
  option = -1
  while option != 0:
    option = inputOption(
      minOptions=0,
      maxOptions=SIZE_MENU, 
      msg=MENU,
    )
    match option:
      case 1:
        grammar: Grammar = reedGrammarFromFile(inputFile)
        grammar.printGrammar()
      case 2:
        grammar: Grammar = reedGrammarFromFile(inputFile)
        grammar.removeLeftRecursion()
        grammar.printGrammar()
        grammar.createFileFromGrammar(OUTPUT_FILE_NAME)
      case 3:
        grammar: Grammar = reedGrammarFromFile(inputFile)
        grammar.removeLeftFactorization()
        grammar.printGrammar()
        grammar.createFileFromGrammar(OUTPUT_FILE_NAME)
      case 4:
        grammar: Grammar = reedGrammarFromFile(inputFile)
        grammar.removeLeftRecursion()
        grammar.removeLeftFactorization()
        grammar.printGrammar()
        grammar.createFileFromGrammar(OUTPUT_FILE_NAME)
      case 5:
        grammar: Grammar = reedGrammarFromFile(inputFile)
        grammar.convertToChomskyForm()
        grammar.printGrammar()
        grammar.createFileFromGrammar(OUTPUT_FILE_NAME)


if __name__ == '__main__':
  main()
