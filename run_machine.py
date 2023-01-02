from base import InputFileManager, LexicalAnalyzer, SyntaxAnalyzer, LL1Machine

with open("input.txt", "r") as f:
    input_manger = InputFileManager(f.read())
lexical_analyzer = LexicalAnalyzer(input_manger)
syntax_analyzer = SyntaxAnalyzer(lexical_analyzer)
syntax_analyzer.parse()

if not syntax_analyzer.valid_ll1:
    print("Grammar is not a valid ll1")
    exit()

input_str = input("please write a input: ")
is_ok = LL1Machine(syntax_analyzer).parse(input_str)
if is_ok:
    print('Input Accepted')
else:
    print("Input Rejected")






