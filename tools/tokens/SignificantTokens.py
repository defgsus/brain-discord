import sys


class SignificantTokens:
    def __init__(self, counter=None, basis=None, factor=2., max_count=200):
        self.max_count = max_count
        self.tokens = None
        self.counter = None
        self.basis = None
        self.factor = None
        if counter:
            self.init(counter, basis, factor, max_count)

    @property
    def index(self):
        return self.basis.index

    def init(self, counter, basis, factor, max_count=200):
        assert counter.tokenizer.index == basis.tokenizer.index
        def _significance(key):
            return -(counter.token_id_freq(key) - factor * basis.token_id_freq(key))
        def _save_div(x, y):
            return x / y if y else 0
        self.max_count = max_count
        token_ids = counter.sorted_keys(key=_significance)
        self.tokens = {
            tok_id: {
                "freq": counter.token_id_freq(tok_id),
                "higher": _save_div(counter.token_id_freq(tok_id), basis.token_id_freq(tok_id)),
                "basefreq": basis.token_id_freq(tok_id)
            }
            for tok_id in token_ids[:self.max_count]
        }
        self.counter = counter
        self.basis = basis
        self.factor = factor
        return self.tokens

    def hitlist_ids(self):
        hitlist = sorted(self.tokens, key=lambda w: -self.tokens[w]["higher"])
        hitlist = [w for w in hitlist if self.tokens[w]["higher"] > 2.]
        return hitlist

    def dump_hitlist(self, num=None, outp=None):
        outp = outp or sys.stdout
        hitlist_ids = self.hitlist_ids()
        if num is not None:
            hitlist_ids = hitlist_ids[:num]

        outp.write("%30s %7s %8s %9s\n" % (
            "token", "higher", "freq", "base freq"
        ))
        for token_id in hitlist_ids:
            h = self.tokens[token_id]

            outp.write("%30s %6sx %8s %9s\n" % (
                self.index.id_to_token(token_id),
                round(h["higher"]),
                "1/%s" % round(1./h["freq"]),
                "1/%s" % round(1./h["basefreq"])
            ))
