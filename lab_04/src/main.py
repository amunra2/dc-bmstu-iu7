from grammer_parser import parse


tests = [
  (
    'a * (b + c)',
    'a b c + *',
  ),
  (
    '1 * 2 + (-3) / 4',
    '1 2 * 0 3 - 4 / +',
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
    '-a + (a - b) * b * c * d <> 0.3',
    '0 a - a b - b * c * d * + 0.3 <>',
  )
]


def main():
  for test in tests:
    print("\n")
    parse(test)


if __name__ == '__main__':
  main()
