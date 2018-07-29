
DEFAULT_STRIP_CHARS = "@#…-'\"„“»«()&"
DEFAULT_SPLIT_CHARS = ",.!?:;\""


class TokenIndex:
    """
    Mapping between str and int.
    Index of all known tokens
    """
    def __init__(self):
        self._token_to_id = dict()
        self._id_to_token = dict()

    def token_to_id(self, tok):
        """
        Get integer id for token.
        If token is not known, an id will be created
        """
        if tok not in self._token_to_id:
            id = len(self._token_to_id) + 1
            self._token_to_id[tok] = id
            self._id_to_token[id] = tok
        return self._token_to_id[tok]

    def id_to_token(self, id, default="?"):
        """Return the token to an id"""
        return self._id_to_token.get(id, default)

    def tokens_to_ids(self, tokens):
        """Convert a list of tokens to a list of ids"""
        return [self.token_to_id(t) for t in tokens]

    def ids_to_tokens(self, ids, default="?"):
        """Convert a list if ids to a list of tokens"""
        return [self.id_to_token(t, default) for t in ids]

    def __contains__(self, item):
        """See if token (str) or token_id (int) is in index"""
        return item in self._id_to_token or item in self._token_to_id

    def __getitem__(self, item):
        """Convert either token to id (str to int), or id to token (int to str), depending on type"""
        if isinstance(item, int):
            return self.id_to_token(item)
        return self.token_to_id(item)

    def to_json(self):
        return {str(i): self._id_to_token[i] for i in self._id_to_token}

    def from_json(self, data):
        self._id_to_token = {int(k): data[k] for k in data}
        self._token_to_id = {self._id_to_token[k]: k for k in self._id_to_token}


class TokenizerBase:
    """
    Basic abstract text tokenizer.
    Subclasses provide the tokenize() function
    """
    def __init__(self, index=None):
        self.index = TokenIndex() if index is None else index

    def tokenize(self, text):
        raise NotImplementedError

    def token_to_id(self, tok):
        return self.index.token_to_id(tok)

    def id_to_token(self, id):
        return self.index.id_to_token(id)

    def tokens_to_ids(self, tokens):
        return self.index.tokens_to_ids(tokens)

    def ids_to_tokens(self, ids):
        return self.index.ids_to_tokens(ids)


class SimpleTokenizer(TokenizerBase):
    """
    It will split a text on any white-char (like python's str.split()) and
    strip any chars from beginning and end of tokens contained in strip_chars.
    """
    def __init__(self,
                 strip_chars=None,
                 index=None,
                 ):
        super(SimpleTokenizer, self).__init__(index=index)
        if strip_chars is not None:
            self.strip_chars = strip_chars
        else:
            self.strip_chars = "".join(set(DEFAULT_STRIP_CHARS + DEFAULT_SPLIT_CHARS))

    def tokenize(self, text):
        tokens = []
        for tok in text.split():
            tok = tok.strip(self.strip_chars)
            if tok:
                tok = self.index.token_to_id(tok)
                tokens.append(tok)
        return tokens


class CharwiseTokenizer(TokenizerBase):
    """
    Full control over whitespace, split, strip and ignore characters.
    """
    def __init__(self,
                 whitespace=None,
                 split=None,
                 strip=None,
                 ignore=None,
                 index=None):
        """
        :param whitespace: a function returning True if the input argument is a white-space char, separating tokens
        :param split: a function returning True if the input argument is a char that separates tokens and should
                      itself be seen as a token
        :param strip: a function returning True if the input argument is a char that should be stripped from
                      the beginning and end of tokens
        :param ignore: a function returning True if the input argument is a char that should be ignored
        :param index: optional TokenIndex instance
        """
        super(CharwiseTokenizer, self).__init__(index=index)
        self.white_func = whitespace or (lambda c: c.isspace())
        self.split_func = split or (lambda c: c in DEFAULT_SPLIT_CHARS)
        self.strip_func = strip or (lambda c: c in DEFAULT_STRIP_CHARS)
        self.ignore_func = ignore or (lambda c: False)

    def tokenize(self, text):
        tokens = []
        def _add(token):
            while token and self.strip_func(token[-1]):
                token = token[:-1]
            if token:
                tokens.append(self.index.token_to_id(token))
        token = ""
        for c in text:
            if self.ignore_func(c):
                continue
            elif self.white_func(c):
                _add(token)
                token = ""
            elif self.split_func(c):
                _add(token)
                tokens.append(self.index.token_to_id(c))
                token = ""
            else:
                if token or not self.strip_func(c):
                    token += c
        _add(token)
        return tokens

