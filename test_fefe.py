from tools.fefe import Fefe

fefe = Fefe()

if 0:
    print(fefe.get_posts_by_year_month(2018, 7))

if 0:
    print(fefe.get_random_post())

if 1:
    posts = fefe.get_all_posts()
    print("num posts: %s" % len(posts))
    text_size = sum(len(p["text"]) for p in posts)
    print("text size in mb: %s" % (text_size // 1024 // 1024))



