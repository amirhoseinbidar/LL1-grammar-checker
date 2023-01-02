import string
from enum import Enum

from tabulate import tabulate

symbol_table = {}


class Empty:
    pass


empty = Empty()
# TODO: check epsilon have to be single rule


class LexemeTypes(Enum):
    OR = ord("|")
    ASSIGN = 257
    NON_TERMINAL = 258
    TERMINAL = 259
    INSTRUCTION_END = 300
    SYNCH = 301
    END = 302


class Error(Exception):
    def __init__(self, message="") -> None:
        self.message = message
        super().__init__(message)

    def throw(self):
        print("\n" + self.__class__.__name__ + " : " + self.message + "\n")
        # exit()
        raise self


class InvalidCharacter(Error):
    def __init__(self, lexical_analyzer) -> None:
        line = lexical_analyzer.line_number + 1
        character_number = (
            lexical_analyzer.input_manager.forward - lexical_analyzer.last_line_start
        )
        message = f"Character '{lexical_analyzer.input_manager.get_char()}' is invalid in line {line}, number {character_number}"
        super().__init__(message)


class InvalidToken(Error):
    def __init__(self, guess, lexical_analyzer) -> None:
        line = lexical_analyzer.line_number + 1
        character_number = (
            lexical_analyzer.input_manager.forward - lexical_analyzer.last_line_start
        )
        message = f"could not recognize token in line {line}, number {character_number}, do you mean '{guess}' ?"
        super().__init__(message)


class InvalidSyntax(Error):
    def __init__(self, syntax_analyzer, description="") -> None:
        line = syntax_analyzer.analyzer.line_number + 1
        character_number = (
            syntax_analyzer.analyzer.input_manager.forward
            - syntax_analyzer.analyzer.last_line_start
        )
        message = f"invalid '{syntax_analyzer.look_ahead.value}' token in line {line}, number {character_number}\n{description}"
        super().__init__(message)


class InvalidSemantic(Error):
    pass


class InvalidLL1Grammar(Exception):
    message = "Grammar is not LL1"


class InputFileManager:
    def __init__(self, input_str) -> None:
        self.input = input_str + "\n"
        self.forward = -1
        self.__end = len(self.input)

    def next_char(self) -> str:
        self.forward += 1
        return self.input[self.forward]

    def retract(self) -> str:
        self.forward -= 1
        return self.input[self.forward]

    def get_char(self) -> str:
        return self.input[self.forward]

    def is_ended(self) -> bool:
        return self.forward + 1 >= self.__end


class Lexeme:
    def __init__(self, value, type) -> None:
        self.value = value
        self.type = type

    def __repr__(self) -> str:
        return f"Lexeme({self.value},{self.type})"

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, Lexeme):
            return self.value == __o.value
        if isinstance(__o, str):
            return self.value == __o
        return super().__eq__(__o)

    def __str__(self) -> str:
        return f"Lex({self.value},{self.type.name})"

    def __repr__(self) -> str:
        return f"Lex({self.value},{self.type.name})"


epsilon = Lexeme("epsilon", LexemeTypes.TERMINAL)
input_end = Lexeme("$", LexemeTypes.TERMINAL)
synch = Lexeme("synch", LexemeTypes.SYNCH)


class LexicalAnalyzer:
    def __init__(self, input_manager) -> None:
        self.input_manager = input_manager
        if not input_manager:
            self.input_manager = InputFileManager()

        self.lexeme_begin = 0
        self.line_number = 0
        self.last_line_start = 0

    def scan_non_terminal(self) -> Lexeme:
        self.lexeme_begin = self.input_manager.forward
        while True:
            char = self.input_manager.next_char()
            if (
                char
                not in string.ascii_letters + string.digits + ">*&!@#%^*()_+=-`~'\""
            ):
                token = self.input_manager.input[
                    self.lexeme_begin : self.input_manager.forward - 1
                ]
                token += ">"
                InvalidToken(token, self).throw()
            if char == ">":
                value = self.input_manager.input[
                    self.lexeme_begin + 1 : self.input_manager.forward
                ]
                return Lexeme(value, LexemeTypes.NON_TERMINAL)

    def scan_one_comment(self) -> None:
        if self.input_manager.next_char() != "/":
            InvalidToken("//", self).throw()
        while True:
            if self.input_manager.next_char() == "\n":
                return self.input_manager.retract()

    def scan_multiple_comment(self) -> None:
        while True:
            if self.input_manager.next_char() == "}":
                return

    def get_token(self) -> Lexeme:
        while True:
            if self.input_manager.is_ended():
                return Lexeme(empty, LexemeTypes.END)

            char = self.input_manager.next_char()

            if char == "-":
                if self.input_manager.next_char() != ">":
                    InvalidToken("->", self).throw()
                return Lexeme("->", LexemeTypes.ASSIGN)
            elif char == ";":
                return Lexeme(";", LexemeTypes.INSTRUCTION_END)
            elif char == "/":
                self.scan_one_comment()
            elif char == "|":
                return Lexeme("|", LexemeTypes.OR)
            elif char == "{":
                self.scan_multiple_comment()
            elif char in string.ascii_letters + string.digits + "*&!@#%^*()_+=-`~'\"":
                return Lexeme(char, LexemeTypes.TERMINAL)
            elif char == "\\":
                char = self.input_manager.next_char()
                if char == "w":
                    return Lexeme(" ", LexemeTypes.TERMINAL)
                elif char == "e":
                    return Lexeme("epsilon", LexemeTypes.TERMINAL)
                InvalidToken("\\w or \\e", self).throw()
            elif char == "<":
                return self.scan_non_terminal()
            elif char in string.whitespace:
                if char == "\n":
                    self.line_number += 1
                    self.last_line_start = self.input_manager.forward
            else:
                InvalidCharacter(self).throw()


class SyntaxAnalyzerBase:
    def __init__(self, lexical_analyzer=None, look_ahead=None):
        self.analyzer = lexical_analyzer
        if not lexical_analyzer:
            self.analyzer = LexicalAnalyzer()
        self.look_ahead = look_ahead

    def match(self, lex_type, value=None, raise_error=False):
        self.next()
        if self.look_ahead.type != lex_type:
            args = (
                self,
                f"Expected {lex_type.name } but got { self.look_ahead.type.name}",
            )
            if raise_error:
                raise InvalidSyntax(*args)
            else:
                InvalidSyntax(*args).throw()
        if value and self.look_ahead.value != value:
            args = (
                self,
                f"Expected {lex_type.name } but got { self.look_ahead.type.name}",
            )
            if raise_error:
                raise InvalidSyntax(*args)
            else:
                InvalidSyntax(*args).throw()

    def next(self):
        self.look_ahead = self.analyzer.get_token()

    def parse(self):
        # subclasses have to provide this method
        raise NotImplemented()


class LL1Machine:
    def __init__(self, syntax_analyzer):
        self.rule_table = syntax_analyzer.rule_table

    def parse(self, input_text):
        input_text = input_text + "$"
        first_rule = symbol_table["rules"][0][0]
        stack = [Lexeme("$", LexemeTypes.TERMINAL), first_rule]
        result = True
        for count, char in enumerate(input_text, 1):
            while True:
                stack_top = stack.pop()
                if stack_top.type == LexemeTypes.TERMINAL:
                    if stack_top == epsilon:
                        continue
                    if stack_top.value == char:
                        break
                    print(
                        f"Expected '{stack_top.value}' but got '{char}' in character number {count}"
                    )
                    if input_end == stack_top:
                        stack = [Lexeme("$", LexemeTypes.TERMINAL), first_rule]
                    result = False
                    continue

                rule_id = self.rule_table[stack_top].get(char)
                if not rule_id:
                    stack.append(stack_top)
                    print(
                        f"SyntaxError: can not parse '{char}' in character number {count}, skipping it"
                    )
                    result = False
                    break
                rule_id = rule_id[0]
                if rule_id == synch:
                    print(
                        f"SyntaxError: can not parse '{char}' in character number {count}, trying new rule"
                    )
                    result = False

                    if len(stack) == 1:
                        stack.append(stack_top)
                        break
                    continue

                rule_copy = list(symbol_table["rules"][rule_id][1])
                rule_copy.reverse()
                stack.extend(rule_copy)

        return result and not stack


class SyntaxAnalyzer(SyntaxAnalyzerBase):
    def __init__(self, lexical_analyzer=None, look_ahead=None):
        super().__init__(lexical_analyzer, look_ahead)
        self.stack = []
        self.analyze_table = {"firsts": {}, "follows": {}, "right_firsts": {}}

    def get_first_of_non_terminal(self, left, rights, rule_id):
        self.analyze_table["firsts"].setdefault(left, set())
        self.analyze_table["right_firsts"].setdefault(rule_id, set())

        if left in self.stack:
            raise InvalidSemantic(
                f"Grammar have left recursion in <{left.value}> non terminal"
            )

        for symbol in rights:
            if symbol.type == LexemeTypes.TERMINAL and symbol != epsilon:
                self.analyze_table["right_firsts"][rule_id].add(symbol)
                self.analyze_table["firsts"][left].add(symbol)
                return

            if symbol.type == LexemeTypes.NON_TERMINAL:
                self.stack.append(left)
                self.get_firsts(symbol)
                self.stack.pop()
                symbol_firsts = self.analyze_table["firsts"][symbol]

                self.analyze_table["firsts"][left].update(symbol_firsts)
                self.analyze_table["right_firsts"][rule_id].update(symbol_firsts)

                if epsilon in symbol_firsts:
                    self.analyze_table["firsts"][left].remove(epsilon)
                    self.analyze_table["right_firsts"][rule_id].remove(epsilon)
                    continue
                else:
                    return

        self.analyze_table["firsts"][left].add(epsilon)
        self.analyze_table["right_firsts"][rule_id].add(epsilon)

    def get_firsts(self, search_symbol=None):
        for rule_id, (left, rights) in enumerate(symbol_table["rules"]):
            if not search_symbol or (search_symbol and left == search_symbol):
                self.get_first_of_non_terminal(left, rights, rule_id)

    def get_follow_of_non_terminal(self, left, rights, search_symbol):
        self.analyze_table["follows"].setdefault(search_symbol, set())
        if search_symbol in self.stack:
            stack_top = self.stack[-1]
            self.analyze_table["follows"][search_symbol].update(
                self.analyze_table["follows"][stack_top]
            )
            self.analyze_table["follows"][stack_top].update(
                self.analyze_table["follows"][search_symbol]
            )
            return

        try:
            left_index = rights.index(search_symbol)
            for symbol in rights[left_index + 1 :]:
                if symbol.type == LexemeTypes.TERMINAL and symbol != epsilon:
                    self.analyze_table["follows"][search_symbol].add(symbol)
                    return
                if symbol.type == LexemeTypes.NON_TERMINAL:
                    firsts = self.analyze_table["firsts"][symbol]
                    self.analyze_table["follows"][search_symbol].update(firsts)
                    if epsilon in firsts:
                        self.analyze_table["follows"][search_symbol].remove(epsilon)
                        continue
                    else:
                        return

            self.stack.append(search_symbol)
            self.get_follows(left)
            self.stack.pop()
            self.analyze_table["follows"][search_symbol].update(
                self.analyze_table["follows"][left]
            )

        except ValueError:
            pass

    def get_follows(self, search_symbol=None):
        for left, rights in symbol_table["rules"]:
            try:
                self.get_follow_of_non_terminal(left, rights, search_symbol)
            except InvalidSemantic:
                return

    def parse_non_terminal(self):
        symbol_table.setdefault("rules", [])
        left_value = self.look_ahead
        self.match(LexemeTypes.ASSIGN)
        right_value = []
        while True:
            self.next()
            if self.look_ahead.type not in [
                LexemeTypes.NON_TERMINAL,
                LexemeTypes.TERMINAL,
                LexemeTypes.INSTRUCTION_END,
                LexemeTypes.OR,
            ]:
                InvalidSyntax(self).throw()
            if self.look_ahead.type == LexemeTypes.INSTRUCTION_END:
                break
            if self.look_ahead.type == LexemeTypes.OR:
                symbol_table["rules"].append((left_value, right_value))
                right_value = []
                continue
            right_value.append(self.look_ahead)

        symbol_table["rules"].append((left_value, right_value))

    def create_rule_table(self):
        self.rule_table = {k: {} for k, _ in symbol_table["rules"]}
        self.valid_ll1 = True
        for idx, (left, _) in enumerate(symbol_table["rules"]):
            for first in self.analyze_table["right_firsts"].get(idx, []):
                if first != epsilon:
                    self.rule_table[left].setdefault(first, [])
                    if len(self.rule_table[left][first]) != 0:
                        self.valid_ll1 = False
                    self.rule_table[left][first].append(idx)
                else:
                    for follow in self.analyze_table["follows"][left]:
                        self.rule_table[left].setdefault(follow, [])
                        if len(self.rule_table[left][follow]) != 0:
                            self.valid_ll1 = False
                        self.rule_table[left][follow].append(idx)

        for idx, (left, _) in enumerate(symbol_table["rules"]):
            for follow in self.analyze_table["follows"].get(left, []):
                if not self.rule_table[left].get(follow, []):
                    self.rule_table[left].setdefault(follow, [])
                    self.rule_table[left][follow].append(synch)

    def print_analyzes(self):
        non_terminal = []
        for k, _ in symbol_table["rules"]:
            if k not in non_terminal:
                non_terminal.append(k)
        print()
        print(
            tabulate(
                [
                    [
                        left,
                        self.analyze_table["firsts"].get(left, ""),
                        self.analyze_table["follows"].get(left, ""),
                    ]
                    for left in non_terminal
                ],
                headers=["Non-Terminal", "First", "Follow"],
                tablefmt="simple_grid",
                stralign="center",
                numalign="center",
            )
        )
        terminals = set()
        for _, rights in symbol_table["rules"]:
            for right_symbol in rights:
                if (
                    right_symbol.type == LexemeTypes.TERMINAL
                    and right_symbol != epsilon
                ):
                    terminals.add(right_symbol)
        headers = list(terminals) + [input_end]
        headers_idx = {i: idx for idx, i in enumerate(headers)}
        table = []
        for non_terminal, rights in self.rule_table.items():
            line = [""] * len(headers)
            for terminal, rule_ids in rights.items():
                line[headers_idx[terminal]] = ", ".join([str(i) for i in rule_ids])
            table.append([non_terminal] + line)

        print(
            tabulate(
                table,
                headers=["Non-Terminal"] + headers,
                tablefmt="simple_grid",
                stralign="center",
                numalign="center",
            )
        )

    def parse(self):
        while True:
            self.next()
            if self.look_ahead.type == LexemeTypes.END:
                break
            elif self.look_ahead.type == LexemeTypes.NON_TERMINAL:
                self.parse_non_terminal()
            else:
                InvalidSyntax(self).throw()

        self.get_firsts()
        self.stack = []
        self.analyze_table["follows"] = {symbol_table["rules"][0][0]: {input_end}}
        for left, _ in symbol_table["rules"]:
            self.get_follows(left)

        self.create_rule_table()
        self.print_analyzes()
