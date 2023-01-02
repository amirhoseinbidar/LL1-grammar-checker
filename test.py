import unittest

import base
from base import (
    InputFileManager,
    Lexeme,
    LexemeTypes,
    LexicalAnalyzer,
    LL1Machine,
    SyntaxAnalyzer,
    epsilon,
    synch,
)


class TestStringMethods(unittest.TestCase):
    def test1(self):
        base.symbol_table = {}
        input_manger = InputFileManager(
            """
            <S> -> <A>a<B>b | <B>b<A>a;
            <A> -> \e;
            <B> -> \e;
        """
        )
        lexical_analyzer = LexicalAnalyzer(input_manger)
        syntax_analyzer = SyntaxAnalyzer(lexical_analyzer)
        syntax_analyzer.parse()
        firsts = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL),
                Lexeme("b", LexemeTypes.TERMINAL),
            },
            Lexeme("A", LexemeTypes.NON_TERMINAL): {epsilon},
            Lexeme("B", LexemeTypes.NON_TERMINAL): {epsilon},
        }
        follows = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("$", LexemeTypes.TERMINAL),
            },
            Lexeme("A", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL),
            },
            Lexeme("B", LexemeTypes.NON_TERMINAL): {
                Lexeme("b", LexemeTypes.TERMINAL),
            },
        }
        rule_table = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL): [0],
                Lexeme("b", LexemeTypes.TERMINAL): [1],
                Lexeme("$", LexemeTypes.NON_TERMINAL): [synch]
            },
            Lexeme("A", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL): [2],
            },
            Lexeme("B", LexemeTypes.NON_TERMINAL): {
                Lexeme("b", LexemeTypes.TERMINAL): [3],
            },
        }
        self.assertDictEqual(syntax_analyzer.analyze_table["firsts"], firsts)
        self.assertDictEqual(syntax_analyzer.analyze_table["follows"], follows)
        self.assertDictEqual(syntax_analyzer.rule_table, rule_table)
        self.assertTrue(syntax_analyzer.valid_ll1)
        ll1_machine = LL1Machine(syntax_analyzer)
        self.assertTrue(ll1_machine.parse("ab"))
        self.assertTrue(ll1_machine.parse("ba"))

    def test2(self):
        base.symbol_table = {}
        input_manger = InputFileManager(
            """
            <S> -> <A><B>;
            <A> -> a | \e;
            <B> -> b | \e;
        """
        )
        lexical_analyzer = LexicalAnalyzer(input_manger)
        syntax_analyzer = SyntaxAnalyzer(lexical_analyzer)
        syntax_analyzer.parse()
        firsts = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL),
                Lexeme("b", LexemeTypes.TERMINAL),
                epsilon,
            },
            Lexeme("A", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL),
                epsilon,
            },
            Lexeme("B", LexemeTypes.NON_TERMINAL): {
                Lexeme("b", LexemeTypes.TERMINAL),
                epsilon,
            },
        }
        follows = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("$", LexemeTypes.TERMINAL),
            },
            Lexeme("A", LexemeTypes.NON_TERMINAL): {
                Lexeme("b", LexemeTypes.TERMINAL),
                Lexeme("$", LexemeTypes.TERMINAL),
            },
            Lexeme("B", LexemeTypes.NON_TERMINAL): {
                Lexeme("$", LexemeTypes.TERMINAL),
            },
        }
        rule_table = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL): [0],
                Lexeme("b", LexemeTypes.TERMINAL): [0],
                Lexeme("$", LexemeTypes.TERMINAL): [0],
            },
            Lexeme("A", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL): [1],
                Lexeme("b", LexemeTypes.TERMINAL): [2],
                Lexeme("$", LexemeTypes.TERMINAL): [2],
            },
            Lexeme("B", LexemeTypes.NON_TERMINAL): {
                Lexeme("b", LexemeTypes.TERMINAL): [3],
                Lexeme("$", LexemeTypes.TERMINAL): [4],
            },
        }
        self.assertDictEqual(syntax_analyzer.analyze_table["firsts"], firsts)
        self.assertDictEqual(syntax_analyzer.analyze_table["follows"], follows)
        self.assertDictEqual(syntax_analyzer.rule_table, rule_table)
        self.assertTrue(syntax_analyzer.valid_ll1)
        ll1_machine = LL1Machine(syntax_analyzer)
        self.assertTrue(ll1_machine.parse("a"))
        self.assertTrue(ll1_machine.parse("b"))
        self.assertTrue(ll1_machine.parse("ab"))
        self.assertTrue(ll1_machine.parse(""))

    def test3(self):
        base.symbol_table = {}
        input_manger = InputFileManager(
            """
            <E> -> <T><E'>;
            <E'> -> +<T><E'> | \e;
            <T> -> <F><T'>;
            <T'> -> *<F><T'> | \e;
            <F> -> (<E>) | i;
        """
        )
        lexical_analyzer = LexicalAnalyzer(input_manger)
        syntax_analyzer = SyntaxAnalyzer(lexical_analyzer)
        syntax_analyzer.parse()
        firsts = {
            Lexeme("E", LexemeTypes.NON_TERMINAL): {
                Lexeme("(", LexemeTypes.TERMINAL),
                Lexeme("i", LexemeTypes.TERMINAL),
            },
            Lexeme("E'", LexemeTypes.NON_TERMINAL): {
                Lexeme("+", LexemeTypes.TERMINAL),
                epsilon,
            },
            Lexeme("T", LexemeTypes.NON_TERMINAL): {
                Lexeme("(", LexemeTypes.TERMINAL),
                Lexeme("i", LexemeTypes.TERMINAL),
            },
            Lexeme("T'", LexemeTypes.NON_TERMINAL): {
                Lexeme("*", LexemeTypes.TERMINAL),
                epsilon,
            },
            Lexeme("F", LexemeTypes.NON_TERMINAL): {
                Lexeme("(", LexemeTypes.TERMINAL),
                Lexeme("i", LexemeTypes.TERMINAL),
            },
        }
        follows = {
            Lexeme("E", LexemeTypes.NON_TERMINAL): {
                Lexeme("$", LexemeTypes.TERMINAL),
                Lexeme(")", LexemeTypes.TERMINAL),
            },
            Lexeme("E'", LexemeTypes.NON_TERMINAL): {
                Lexeme("$", LexemeTypes.TERMINAL),
                Lexeme(")", LexemeTypes.TERMINAL),
            },
            Lexeme("T", LexemeTypes.NON_TERMINAL): {
                Lexeme("$", LexemeTypes.TERMINAL),
                Lexeme(")", LexemeTypes.TERMINAL),
                Lexeme("+", LexemeTypes.TERMINAL),
            },
            Lexeme("T'", LexemeTypes.NON_TERMINAL): {
                Lexeme("$", LexemeTypes.TERMINAL),
                Lexeme(")", LexemeTypes.TERMINAL),
                Lexeme("+", LexemeTypes.TERMINAL),
            },
            Lexeme("F", LexemeTypes.NON_TERMINAL): {
                Lexeme(")", LexemeTypes.TERMINAL),
                Lexeme("$", LexemeTypes.TERMINAL),
                Lexeme("+", LexemeTypes.TERMINAL),
                Lexeme("*", LexemeTypes.TERMINAL),
            },
        }
        rule_table = {
            Lexeme("E", LexemeTypes.NON_TERMINAL): {
                Lexeme("(", LexemeTypes.TERMINAL): [0],
                Lexeme("i", LexemeTypes.TERMINAL): [0],
                Lexeme(")", LexemeTypes.TERMINAL): [synch],
                Lexeme("$", LexemeTypes.TERMINAL): [synch],
            },
            Lexeme("E'", LexemeTypes.NON_TERMINAL): {
                Lexeme("+", LexemeTypes.TERMINAL): [1],
                Lexeme(")", LexemeTypes.TERMINAL): [2],
                Lexeme("$", LexemeTypes.TERMINAL): [2],
            },
            Lexeme("T", LexemeTypes.NON_TERMINAL): {
                Lexeme("i", LexemeTypes.TERMINAL): [3],
                Lexeme("(", LexemeTypes.TERMINAL): [3],
                Lexeme("+", LexemeTypes.TERMINAL): [synch],
                Lexeme(")", LexemeTypes.TERMINAL): [synch],
                Lexeme("$", LexemeTypes.TERMINAL): [synch],
            },
            Lexeme("T'", LexemeTypes.NON_TERMINAL): {
                Lexeme("$", LexemeTypes.TERMINAL): [5],
                Lexeme(")", LexemeTypes.TERMINAL): [5],
                Lexeme("+", LexemeTypes.TERMINAL): [5],
                Lexeme("*", LexemeTypes.TERMINAL): [4],
            },
            Lexeme("F", LexemeTypes.NON_TERMINAL): {
                Lexeme("(", LexemeTypes.TERMINAL): [6],
                Lexeme("i", LexemeTypes.TERMINAL): [7],
                Lexeme("+", LexemeTypes.TERMINAL): [synch],
                Lexeme("*", LexemeTypes.TERMINAL): [synch],
                Lexeme(")", LexemeTypes.TERMINAL): [synch],
                Lexeme("$", LexemeTypes.TERMINAL): [synch],
            },
        }

        self.assertDictEqual(syntax_analyzer.analyze_table["firsts"], firsts)
        self.assertDictEqual(syntax_analyzer.analyze_table["follows"], follows)
        self.assertDictEqual(syntax_analyzer.rule_table, rule_table)
        self.assertTrue(syntax_analyzer.valid_ll1)
        ll1_machine = LL1Machine(syntax_analyzer)
        self.assertTrue(ll1_machine.parse("i+i*i"))
        self.assertTrue(ll1_machine.parse("i+(i+i)*i"))
        self.assertTrue(ll1_machine.parse("(i*i)+i"))
        self.assertTrue(ll1_machine.parse("i*i*i*i"))
        self.assertTrue(ll1_machine.parse("i*i*(i*i)+i"))
        self.assertFalse(ll1_machine.parse(")i*+i"))


    def test4(self):
        base.symbol_table = {}
        input_manger = InputFileManager(
            """
            <S> -> i<E>t<S><S'> | a;
            <S'> -> e<S> | \e;
            <E> -> b;
            """
        )
        lexical_analyzer = LexicalAnalyzer(input_manger)
        syntax_analyzer = SyntaxAnalyzer(lexical_analyzer)
        syntax_analyzer.parse()
        firsts = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("i", LexemeTypes.TERMINAL),
                Lexeme("a", LexemeTypes.TERMINAL),
            },
            Lexeme("S'", LexemeTypes.NON_TERMINAL): {
                Lexeme("e", LexemeTypes.TERMINAL),
                epsilon,
            },
            Lexeme("E", LexemeTypes.NON_TERMINAL): {
                Lexeme("b", LexemeTypes.TERMINAL),
            },
        }
        follows = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("$", LexemeTypes.TERMINAL),
                Lexeme("e", LexemeTypes.TERMINAL),
            },
            Lexeme("S'", LexemeTypes.NON_TERMINAL): {
                Lexeme("e", LexemeTypes.TERMINAL),
                Lexeme("$", LexemeTypes.TERMINAL),
            },
            Lexeme("E", LexemeTypes.NON_TERMINAL): {
                Lexeme("t", LexemeTypes.TERMINAL),
            },
        }
        rule_table = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("i", LexemeTypes.TERMINAL): [0],
                Lexeme("a", LexemeTypes.TERMINAL): [1],
                Lexeme("e", LexemeTypes.TERMINAL): [synch],
                Lexeme("$", LexemeTypes.TERMINAL): [synch],
            },
            Lexeme("S'", LexemeTypes.NON_TERMINAL): {
                Lexeme("e", LexemeTypes.TERMINAL): [2, 3],
                Lexeme("$", LexemeTypes.TERMINAL): [3],
            },
            Lexeme("E", LexemeTypes.NON_TERMINAL): {
                Lexeme("b", LexemeTypes.TERMINAL): [4],
                Lexeme("t", LexemeTypes.TERMINAL): [synch],
            },
        }
        self.assertDictEqual(syntax_analyzer.analyze_table["firsts"], firsts)
        self.assertDictEqual(syntax_analyzer.analyze_table["follows"], follows)
        self.assertDictEqual(syntax_analyzer.rule_table, rule_table)
        self.assertFalse(syntax_analyzer.valid_ll1)

    def test5(self):
        base.symbol_table = {}
        input_manger = InputFileManager(
            """
            <S> -> <A>a;
            <A> -> <B><D>;
            <B> -> b;
            <B> -> \e;
            <D> -> d;
            <D> -> \e;
            """
        )
        lexical_analyzer = LexicalAnalyzer(input_manger)
        syntax_analyzer = SyntaxAnalyzer(lexical_analyzer)
        syntax_analyzer.parse()
        firsts = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("b", LexemeTypes.TERMINAL),
                Lexeme("a", LexemeTypes.TERMINAL),
                Lexeme("d", LexemeTypes.TERMINAL),
            },
            Lexeme("A", LexemeTypes.NON_TERMINAL): {
                Lexeme("b", LexemeTypes.TERMINAL),
                Lexeme("d", LexemeTypes.TERMINAL),
                epsilon,
            },
            Lexeme("B", LexemeTypes.NON_TERMINAL): {
                Lexeme("b", LexemeTypes.TERMINAL),
                epsilon,
            },
            Lexeme("D", LexemeTypes.NON_TERMINAL): {
                Lexeme("d", LexemeTypes.TERMINAL),
                epsilon,
            },
        }
        follows = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("$", LexemeTypes.TERMINAL),
            },
            Lexeme("A", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL),
            },
            Lexeme("B", LexemeTypes.NON_TERMINAL): {
                Lexeme("d", LexemeTypes.TERMINAL),
                Lexeme("a", LexemeTypes.TERMINAL),
            },
            Lexeme("D", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL),
            },
        }
        rule_table = {
            Lexeme("S", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL): [0],
                Lexeme("d", LexemeTypes.TERMINAL): [0],
                Lexeme("b", LexemeTypes.TERMINAL): [0],
                Lexeme("$", LexemeTypes.TERMINAL): [synch],
            },
            Lexeme("A", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL): [1],
                Lexeme("d", LexemeTypes.TERMINAL): [1],
                Lexeme("b", LexemeTypes.TERMINAL): [1],
            },
            Lexeme("B", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL): [3],
                Lexeme("d", LexemeTypes.TERMINAL): [3],
                Lexeme("b", LexemeTypes.TERMINAL): [2],
            },
            Lexeme("D", LexemeTypes.NON_TERMINAL): {
                Lexeme("a", LexemeTypes.TERMINAL): [5],
                Lexeme("d", LexemeTypes.TERMINAL): [4],
            },
        }
        self.assertDictEqual(syntax_analyzer.analyze_table["firsts"], firsts)
        self.assertDictEqual(syntax_analyzer.analyze_table["follows"], follows)
        self.assertDictEqual(syntax_analyzer.rule_table, rule_table)
        self.assertTrue(syntax_analyzer.valid_ll1)
        ll1_machine = LL1Machine(syntax_analyzer)
        self.assertTrue(ll1_machine.parse("ba"))
        self.assertTrue(ll1_machine.parse("a"))
        self.assertTrue(ll1_machine.parse("da"))

if __name__ == "__main__":
    unittest.main()
