from tools.fefe import Fefe
from tools.tokens import TokenCounter


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
    counter = TokenCounter()
    posts = fefe.get_all_posts()
    for p in posts:
        counter.add_text(p["text"])
    counter.dump_hitlist(100)


