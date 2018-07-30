

class TokenRelation:

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self._relations = dict()
        self._back_relations = dict()

    @property
    def index(self):
        return self.tokenizer.index

    def add_relation(self, token_id_1, token_id_2, weight=1.):
        if token_id_1 not in self._relations:
            self._relations[token_id_1] = {token_id_2: weight}
        else:
            rel = self._relations[token_id_1]
            rel[token_id_2] = rel.get(token_id_2, 0.) + weight

        if token_id_2 not in self._back_relations:
            self._back_relations[token_id_2] = {token_id_1: weight}
        else:
            rel = self._back_relations[token_id_2]
            rel[token_id_1] = rel.get(token_id_1, 0.) + weight

    def add_relations(self, token_ids, weight=1.):
        for i in range(len(token_ids)):
            for j in range(i+1, len(token_ids)):
                self.add_relation(token_ids[i], token_ids[j], weight)

    def get_relations(self, token_id):
        if token_id in self._relations:
            return self._relations[token_id]
        if token_id in self._back_relations:
            return self._back_relations[token_id]
        return None

