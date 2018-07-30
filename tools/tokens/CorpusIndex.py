from .tokenizer import SimpleTokenizer
from .TokenCounter import TokenCounter
from .TokenRelation import TokenRelation

class CorpusIndex:

    def __init__(self, tokenizer=None):
        self.tokenizer = tokenizer or SimpleTokenizer()
        self._documents = dict()
        self._base_counter = TokenCounter(tokenizer=self.tokenizer)
        self._relation = TokenRelation(tokenizer=self.tokenizer)
        self._token_id_to_document_ids = dict()

    @property
    def index(self):
        return self.tokenizer.index

    def add_document(self, key, text):
        token_ids = self.tokenizer.tokenize(text)
        self._documents[key] = {
            "token_ids": token_ids,
            "length": len(token_ids),
        }
        self._base_counter.add_token_ids(token_ids)

    def build_index(self):
        for document_id in self._documents:
            token_ids = self._documents[document_id]["token_ids"]
            counter = TokenCounter(tokenizer=self.tokenizer)
            counter.add_token_ids(token_ids)
            significant_ids = [
                id for id in token_ids
                if counter.token_id_freq(id) >= 20. * self._base_counter.token_id_freq(id)
            ]
            self._documents[document_id]["significant_ids"] = significant_ids
            self._relation.add_relations(significant_ids)
            #print(self.index.ids_to_tokens(significant_ids))
            for token_id in token_ids:
                if token_id not in self._token_id_to_document_ids:
                    self._token_id_to_document_ids[token_id] = {document_id}
                else:
                    self._token_id_to_document_ids[token_id].add(document_id)
        self._relation.remove_below(2.)

    def document_ids_for_token_id(self, token_id):
        return self._token_id_to_document_ids.get(token_id)

    def document_ids_for_token(self, token):
        return self._token_id_to_document_ids.get(self.index.token_to_id(token))

    def weighted_document_ids_for_token_id(self, token_id):
        relations = self._relation.get_relations(token_id)
        if not relations:
            relations = {token_id: 1.}
        else:
            relations = relations.copy()
            max_relation = max(relations.values()) * 2.
            relations[token_id] = max_relation

        document_id_weights = dict()
        for token_id in relations:
            document_ids = self.document_ids_for_token_id(token_id)
            if document_ids:
                for document_id in document_ids:
                    document_id_weights[document_id] = document_id_weights.get(document_id, 0.) + relations[token_id]

        for document_id in document_id_weights:
            document_id_weights[document_id] /= 1. + .02 * self._documents[document_id]["length"]

        return None if not document_id_weights else document_id_weights

    def weighted_document_ids_for_token(self, token):
        return self.weighted_document_ids_for_token_id(self.index.token_to_id(token))

    def weighted_document_ids_for_tokens_AND(self, tokens):
        all_document_ids = dict()
        per_token_document_ids = []
        for tok in tokens:
            doc_ids = self.weighted_document_ids_for_token(tok)
            per_token_document_ids.append(doc_ids)
            for doc_id in doc_ids:
                all_document_ids[doc_id] = all_document_ids.get(doc_id, 0) + doc_ids[doc_id]

        and_ids = dict()
        for document_id in all_document_ids:
            add_it = True
            for token_document_ids in per_token_document_ids:
                if document_id not in token_document_ids:
                    add_it = False
                    break
            if add_it:
                and_ids[document_id] = all_document_ids[document_id]
        return and_ids