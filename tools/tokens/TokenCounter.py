import json
import sys

from .tokenizer import SimpleTokenizer


class TokenCounter:
    """
    Simple counter of tokens in a corpus.
    It stores the count for each token_id in self.count
    and the overall number of tokens in self.num_all
    """
    def __init__(self, tokenizer=None):
        self.num_all = 0
        self.count = dict()
        self.tokenizer = tokenizer or SimpleTokenizer()

    @property
    def index(self):
        return self.tokenizer.index

    def sorted_keys(self, key=None):
        return sorted(self.count, key=key or (lambda k: -self.count[k]))

    def token_count(self, token):
        """Return count of a token, or zero"""
        if token not in self.index:
            return 0
        return self.token_id_count(self.index.token_to_id(token))

    def token_id_count(self, token_id):
        """Return count of a token_id, or zero"""
        if token_id not in self.index:
            return 0
        return self.count.get(token_id, 0)

    def token_freq(self, token):
        """Return frequency of a token (between 0 and 1)"""
        return self.token_id_freq(self.index.token_to_id(token))

    def token_id_freq(self, token_id):
        """Return frequency of a token-id (between 0 and 1)"""
        return 0 if not self.num_all else self.count.get(token_id, 0) / self.num_all

    def add_token(self, token, num=1, num_all=1):
        """
        Add a token
        Adds `num` to the token counter and `num_all` to the num_all-counter
        """
        self.add_token_id(self.index.token_to_id(token), num=num, num_all=num_all)

    def add_token_id(self, token_id, num=1, num_all=1):
        """
        Add a token_id
        Adds `num` to the token counter and `num_all` to the num_all-counter
        """
        self.count[token_id] = self.count.get(token_id, 0) + num
        self.num_all += num_all

    def add_text(self, text, num=1, num_all=1):
        """
        Adds all the tokens of a text, using self.tokenizer
        """
        token_ids = self.tokenizer.tokenize(text)
        self.add_token_ids(token_ids, num=num, num_all=num_all)

    def add_token_ids(self, token_ids, num=1, num_all=1):
        """
        Adds all token_ids
        """
        for t in token_ids:
            self.add_token_id(t, num, num_all)

    def to_json(self):
        return {
            "index": self.tokenizer.index.to_json(),
            "num": self.num_all,
            "count": self.count,
        }

    def from_json(self, data):
        self.tokenizer.index.from_json(data["index"])
        self.num_all = data["num"]
        self.count = data["count"]

    def save(self, fn):
        with open(fn, "w") as f:
            json.dump(self.to_json(), f)

    def load(self, fn):
        with open(fn) as f:
            self.from_json(json.load(f))

    def dump_hitlist(self, max_num=20, sort_key=None, outp=None):
        outp = outp or sys.stdout
        hitlist = sorted(self.count, key=sort_key or (lambda k: -self.count[k]))
        hitlist = hitlist[:max_num]
        outp.write("%s scanned tokens\n" % self.num_all)
        outp.write("%s unique tokens (%s%%)\n" % (len(self.count), round(len(self.count) / self.num_all * 100, 2)))
        outp.write("%10s | %8s | %s\n" % ("count", "freq", "token"))
        for token_id in hitlist:
            outp.write("%10s | %8s | %s\n" % (
                round(self.count[token_id],2),
                "1/%s" % round(self.num_all / self.count[token_id]),
                self.index.id_to_token(token_id),
            ))

    def subtracted(self, counter, fac):
        ret = TokenCounter()
        ret.num_all = self.num_all
        for w in self.count:
            if w in counter.count:
                p1 = self.count[w] / self.num_all
                p2 = counter.count[w] / counter.num_all
                p1 -= p2 * fac
                ret.count[w] = p1 * self.num_all
        return ret
