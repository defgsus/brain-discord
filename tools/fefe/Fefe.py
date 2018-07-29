import os
import sys
import datetime
import random

from .download import download_fefe
from .parse import parse_blog_html


class Fefe(object):

    CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fefe-html-cache")

    def __init__(self):
        self._posts_per_month = dict()

    def get_posts_by_year_month(self, year, month):
        key = (year, month)
        if key not in self._posts_per_month:
            filename = download_fefe(year, month, cache_dir=self.CACHE_DIR)
            with open(filename, "r") as fp:
                posts = parse_blog_html(fp.read())

                self._posts_per_month[key] = posts

        return self._posts_per_month[key]

    def get_post(self, year, month, day, count):
        posts = self.get_posts_by_year_month(year, month)
        for p in posts:
            if p["date"].day == day and p["day_index"] == count:
                return p
        return None

    def get_random_post(self, year=None, month=None, day=None):
        while True:
            ryear = year or random.randrange(2005, datetime.date.today().year+1)
            rmonth = month or random.randrange(3 if year==2005 else 1, 13)
            posts = self.get_posts_by_year_month(ryear, rmonth)
            if day:
                posts = [p for p in posts if p["date"].day == day]
                if not posts:
                    return None
            if posts:
                break

        return None if not posts else posts[random.randrange(len(posts))]

    def render_post_to_discord(self, post):
        print(post)

        inserts = []
        for tag in post["tags"]:
            start, end = tag["i"]
            name = tag["tag"]
            if name == "i":
                inserts.append([start, "*"])
                inserts.append([end, "*"])
            elif name in ("b", "a"):
                inserts.append([start, "**"])
                inserts.append([end, "**"])
            elif name == "p":
                inserts.append([end, "\n"])
            elif name in ("pre", "blockquote"):
                inserts.append([start, "```\n"])
                inserts.append([end, "```"])

        text = post["text"]
        if not inserts:
            markup = text
        else:
            markup = ""
            text_index = 0
            for insert_pos, insert_what in inserts:
                markup += text[text_index:insert_pos]
                markup += insert_what
                text_index = insert_pos
            if text_index < len(text):
                markup += text[text_index:]

        links = [tag["url"] for tag in post["tags"] if tag["tag"] == "a"]
        for i, link in enumerate(links):
            if link.startswith("/?"):
                links[i] = "http://blog.fefe.de%s" % link
            if link.startswith("//"):
                links[i] = "http:%s" % link

        links = "\n".join(links)

        markup = "`%s`\n%s\n%s" % (post["date"], markup, links)

        return markup
