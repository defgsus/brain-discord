from .wordcounter import tokenize
from tools.syntax.wiktionary import Wiktionary


class WordRelations:

    def __init__(self, wiktionary=None):
        self.relations = dict()
        self._wiktionary = wiktionary

    @property
    def wiktionary(self):
        if self._wiktionary is None:
            self._wiktionary = Wiktionary()
            self._wiktionary.load()
        return self._wiktionary

    def normalize(self, token):
        return self.wiktionary.get_baseform(token)

    def add_relation(self, a, b, strength=1, normalize=False):
        if normalize:
            a = self.normalize(a)
            b = self.normalize(b)
        for i in range(2):
            if a not in self.relations:
                self.relations[a] = {b: strength}
            else:
                self.relations[a][b] = self.relations[a].get(b, 0) + strength
            a, b = b, a

    def add_tokens(self, tokens, strength=1, normalize=False):
        """Relate each with each token"""
        if normalize:
            tokens = [self.normalize(t) for t in tokens]
        for i in range(len(tokens)):
            for j in range(i+1, len(tokens)):
                t1, t2 = tokens[i], tokens[j]
                if t1 != t2:
                    self.add_relation(t1, t2, normalize=False)

    def hitlist(self, reduce=max):
        return sorted(self.relations, key=lambda a: -reduce(self.relations[a].values()))

    def dump_hitlist(self, num=10, numx=10, reduce=max):
        hitlist = self.hitlist(reduce=reduce)
        for a in hitlist[:num]:
            s = "%s" % a
            for b in sorted(self.relations[a], key=lambda b: -self.relations[a][b])[:numx]:
                s += " (%s)%s" % (self.relations[a][b], b)

    def dump_hitlist_html(self, num=100, numx=10):
        hitlist = self.hitlist()
        markup = '<div>'
        for a in hitlist[:num]:
            markup += '<p><big>%s <b>%s</b></big><br>' % (sum(self.relations[a].values()), a)
            for b in sorted(self.relations[a], key=lambda b: -self.relations[a][b])[:numx]:
                markup += " (%s)<b>%s</b>" % (self.relations[a][b], b)
            markup += '</p>'
        markup += '</div>'
        return markup

    def get_dataframe(self, num=None, normalize=True, reduce=sum):
        import pandas
        hitlist = self.hitlist(reduce=reduce)
        if num is not None:
            hitlist = hitlist[:num]
        rows = []
        max_val = 0
        for tok in hitlist:
            rel = self.relations[tok]
            rows.append([rel.get(rtok, 0) for rtok in hitlist])
            max_val = max(max_val, max(rows[-1]))
        pd = pandas.DataFrame(rows, columns=hitlist, index=hitlist)
        if normalize:
            pd /= max_val
        return pd