from grammer_parser import tokenize, parse


code = '''
begin
  a := 23 <> (-1830 + not(-45));
  b := (a * 2) and (88 mod 3);
  d := not (100.0 / (25 + 43) - 25 * 0.023)
end
'''




def main():
  tokens = tokenize(code)
  print(tokens)
  parse(tokens)


if __name__ == '__main__':
  main()
