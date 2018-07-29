import unittest

from tools.tokens.tokenizer import *
from tools.tokens.TokenCounter import TokenCounter


class TestTokenIndex(unittest.TestCase):

    def test_index(self):
        idx = TokenIndex()
        a = idx.token_to_id("a")
        b = idx.token_to_id("b")
        [c, d, e] = idx.tokens_to_ids(["c", "d", "e"])
        self.assertEqual(a, idx.token_to_id("a"))
        self.assertEqual(b, idx.token_to_id("b"))
        self.assertEqual(c, idx.token_to_id("c"))
        self.assertEqual(d, idx.token_to_id("d"))
        self.assertEqual(e, idx.token_to_id("e"))
        self.assertEqual([a, b, c, d, e], idx.tokens_to_ids(["a", "b", "c", "d", "e"]))

    def test_get_method(self):
        idx = TokenIndex()
        a = idx["a"]
        b = idx["b"]
        self.assertEqual(a, idx["a"])
        self.assertEqual(b, idx["b"])
        self.assertEqual("a", idx[a])
        self.assertEqual("b", idx[b])


TEXT_1 = """
Hallo, das ist ein Test!
irgend-welcher "formatierter" Text...
"""


class TestSimpleTokenizer(unittest.TestCase):

    def test_default(self):
        tokenizer = SimpleTokenizer()
        tokens = tokenizer.tokenize(TEXT_1)
        self.assertEqual(8, len(tokens))
        self.assertEqual(8, len(set(tokens)))
        self.assertEqual(['Hallo', 'das', 'ist', 'ein', 'Test',
                          'irgend-welcher', 'formatierter', 'Text'],
                         tokenizer.ids_to_tokens(tokens))


class TestCharwiseTokenizer(unittest.TestCase):

    def test_default(self):
        tokenizer = CharwiseTokenizer()
        tokens = tokenizer.tokenize(TEXT_1)
        #print(tokenizer.ids_to_tokens(set(tokens)))
        self.assertEqual(15, len(tokens))
        self.assertEqual(12, len(set(tokens)))
        self.assertEqual(['Hallo', ',', 'das', 'ist', 'ein', 'Test', '!',
                          'irgend-welcher', '"', 'formatierter', '"',
                          'Text', '.', '.', '.'],
                         tokenizer.ids_to_tokens(tokens))


TEXT_2 = """
Ein Text mit Wiederholungen! Weil, Wiederholungen sind auch wichtig.
Gerade im Text. Dort sind Wiederholungen ganz wichtig!
"""


class TestTokenCounter(unittest.TestCase):

    def test_counter_with_default_tokenizer(self):
        counter = TokenCounter()
        counter.add_text(TEXT_2)

        self.assertEqual(17, counter.num_all)
        self.assertEqual(3, counter.token_count("Wiederholungen"))
        self.assertEqual(2, counter.token_count("Text"))
        self.assertEqual(2, counter.token_count("sind"))
        self.assertEqual(2, counter.token_count("wichtig"))
        self.assertEqual(1, counter.token_count("ganz"))

        self.assertEqual(3./17., counter.token_freq("Wiederholungen"))
