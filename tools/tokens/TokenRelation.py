

class TokenRelation:

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self._relations = dict()

    @property
    def index(self):
        return self.tokenizer.index

    def add_relation(self, token_id_1, token_id_2, weight=1.):
        def _add(token_id_1, token_id_2):
            if token_id_1 not in self._relations:
                self._relations[token_id_1] = {token_id_2: weight}
            else:
                rel = self._relations[token_id_1]
                rel[token_id_2] = rel.get(token_id_2, 0.) + weight
        _add(token_id_1, token_id_2)
        _add(token_id_2, token_id_1)

    def add_relations(self, token_ids, weight=1.):
        for i in range(len(token_ids)):
            for j in range(i+1, len(token_ids)):
                self.add_relation(token_ids[i], token_ids[j], weight)

    def remove_below(self, weight):
        new_relations = dict()
        for tok_id_1 in self._relations:
            new_rel = dict()
            rel = self._relations[tok_id_1]
            for tok_id_2 in rel:
                if rel[tok_id_2] >= weight:
                    new_rel[tok_id_2] = rel[tok_id_2]
            if new_rel:
                new_relations[tok_id_1] = new_rel
        self._relations = new_relations

    def get_relations(self, token_id):
        return self._relations.get(token_id)

