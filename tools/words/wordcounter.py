import json

from .tokenizer import SimpleTokenizer


class Counter:
    def __init__(self, tokenizer=None):
        self.num_all = 0
        self.count = dict()
        self.tokenizer = tokenizer or SimpleTokenizer()

    def sorted_keys(self, key=None):
        return sorted(self.count, key=key or (lambda k: -self.count[k]))

    def freq(self, item):
        return 0 if not self.num_all else self.count.get(item, 0) / self.num_all

    def add(self, token, num=1, num_all=1):
        self.count[token] = self.count.get(token, 0) + num
        self.num_all += num_all

    def add_text(self, text, num=1, num_all=1):
        tokens = self.tokenizer.tokenize(text)
        for t in tokens:
            self.add(t, num, num_all)

    def save(self, fn):
        with open(fn, "w") as f:
            json.dump({
                "index": self.tokenizer.index.to_json(),
                "num": self.num_all,
                "count": self.count,
            }, f)

    def load(self, fn):
        with open(fn) as f:
            d = json.load(f)
            self.tokenizer.index.from_json(d["index"])
            self.num_all = d["num"]
            self.count = d["count"]

    def dump_hitlist(self, max_num=20, sort_key=None):
        hitlist = sorted(self.count, key=sort_key or (lambda k: -self.count[k]))
        hitlist = hitlist[:max_num]
        print("%s scanned items" % self.num_all)
        print("%s unique items (%s%%)" % (len(self.count), round(len(self.count) / self.num_all * 100, 2)))
        for word in hitlist:
            print("%10s  %8s  %s" % (round(self.count[word],2), "1/%s" % round(self.num_all / self.count[word]), word))

    def subtracted(self, counter, fac):
        ret = Counter()
        ret.num_all = self.num_all
        for w in self.count:
            if w in counter.count:
                p1 = self.count[w] / self.num_all
                p2 = counter.count[w] / counter.num_all
                p1 -= p2 * fac
                ret.count[w] = p1 * self.num_all
        return ret


class SignificantWords:
    def __init__(self, counter=None, basis=None, factor=None):
        self.words = None
        self.counter = None
        self.basis = None
        self.factor = None
        if counter:
            self.init(counter, basis, factor)

    def init(self, counter, basis, factor):
        def _significance(key):
            return -(counter.freq(key) - factor*basis.freq(key))
        def _save_div(x, y):
            return x / y if y else 0
        self.words = counter.sorted_keys(key=_significance)
        self.words = {k: {"freq": counter.freq(k),
                          "higher": _save_div(counter.freq(k), basis.freq(k)),
                          "basefreq": basis.freq(k)}
                      for k in self.words[:200]}
        self.counter = counter
        self.basis = basis
        self.factor = factor
        return self.words

    def hitlist(self):
        hitlist = sorted(self.words, key=lambda w: -self.words[w]["higher"])
        hitlist = [w for w in hitlist if self.words[w]["higher"] > 2.]
        ignore = set()
        for w in hitlist:
            for w2 in hitlist:
                if w2 != w and w in w2:
                    ignore.add(w2)
        hitlist = [w for w in hitlist if w not in ignore]
        return hitlist

    def dump_hitlist(self, num=None):
        hitlist = self.hitlist()
        if num is not None:
            hitlist = hitlist[:num]
        for word in hitlist:
            h = self.words[word]

            outp = "%30s %6sx %8s %8s" % (
                word, round(h["higher"]),
                "1/%s" % round(1./h["freq"]),
                "1/%s" % round(1./h["basefreq"])
            )
            print(outp)
