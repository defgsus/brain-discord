from tools.fefe import Fefe
from tools.tokens import TokenCounter, SignificantTokens, CorpusIndex


fefe = Fefe()

if 0:
    print(fefe.get_posts_by_year_month(2018, 7))

if 0:
    print(fefe.get_random_post())

if 0:
    posts = fefe.get_all_posts()
    print("num posts: %s" % len(posts))
    text_size = sum(len(p["text"]) for p in posts)
    print("text size in mb: %s" % (text_size // 1024 // 1024))

if 0:
    counter_base = TokenCounter()
    #posts = fefe.get_all_posts()
    posts = fefe.get_posts_by_year(2017)
    for p in posts:
        p["textl"] = p["text"].lower()
        counter_base.add_text(p["textl"])
    counter_base.dump_hitlist(100)

    for p in posts:
        print("-"*50)
        counter = TokenCounter(tokenizer=counter_base.tokenizer)
        counter.add_text(p["textl"])
        significant = SignificantTokens(counter, counter_base, 2.)
        significant.dump_hitlist()

if 0:
    corpus = CorpusIndex()
    print("getting posts...")
    posts = fefe.get_posts_by_year(2017)
    for p in posts:
        p["textl"] = p["text"].lower()
        p["key"] = "%s-%s" % (p["date"].strftime("%Y-%m-%d"), p["day_index"])
        corpus.add_document(p["key"], p["textl"])
    print("building index")
    corpus.build_index()

    #print(corpus.document_ids_for_token("mafia"))
    relations = corpus._relation.get_relations(corpus.index.token_to_id("virus"))
    for token_id in sorted(relations, key=lambda x: relations[x]):
        print(relations[token_id], corpus.index.id_to_token(token_id))

    weighted_docs = corpus.weighted_document_ids_for_token("karikatur")
    if weighted_docs:
        print(", ".join("%s:%s" % (key, weighted_docs[key]) for key in sorted(weighted_docs, key=lambda x: weighted_docs[x])))

if 1:
    fefe = Fefe()
    posts = fefe.search_posts("menschenleben")
    print(posts)