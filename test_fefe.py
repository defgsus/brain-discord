from tools.fefe import Fefe
from tools.tokens import TokenCounter, SignificantTokens


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

if 1:
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

