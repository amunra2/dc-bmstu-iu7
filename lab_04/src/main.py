from grammer_parser import parse


tests = [
  (
    'a * (b + c)',
    'a b c + *',
  ),
  (
    'a + b * c',
    'a b c * +',
  ),
  (
    '(a + b) * c',
    'a b + c *',
  ),
  (
    'a * (b + c)',
    'a b c + *',
  ),
  (
    '5 * 7 + (-9) / 11',
    '5 7 * 0 9 - 11 / +',
  ),
  (
    '-a + (a - b) * b * c * d <> 0.23',
    '0 a - a b - b * c * d * + 0.23 <>',
  )
]


def main():
  for test in tests:
    print("\n")
    parse(test)


if __name__ == '__main__':
  main()
