import os
import sys
import datetime
import random

from .download import download_fefe
from .parse import parse_blog_html
from tools.tokens import CorpusIndex


class Fefe(object):

    CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fefe-html-cache")

    def __init__(self):
        self._posts_per_month = dict()
        self._corpus = None

    def _build_index(self):
        from settings import FEFE_INDEX
        print("building fefe index")
        if isinstance(FEFE_INDEX, (tuple, list)):
            posts = []
            for year in FEFE_INDEX:
                posts += self.get_posts_by_year(year)
        elif isinstance(FEFE_INDEX, int):
            posts = self.get_posts_by_year(FEFE_INDEX)
        elif FEFE_INDEX == "all":
            posts = self.get_all_posts()
        else:
            raise ValueError("Invalid FEFE_INDEX '%s'" % FEFE_INDEX)

        for p in posts:
            p["key"] = "%s-%s" % (p["date"].strftime("%Y-%m-%d"), p["day_index"])
            self._corpus.add_document(p["key"], p["text"].lower())
        self._corpus.build_index()

    def get_posts_by_year_month(self, year, month):
        if not 2005 <= year <= datetime.date.today().year:
            return None
        if not 1 <= month <= 12:
            return None
        if year == 2005 and month < 3:
            return None
        key = (year, month)
        if key not in self._posts_per_month:
            filename = download_fefe(year, month, cache_dir=self.CACHE_DIR)
            with open(filename, "r") as fp:
                posts = parse_blog_html(fp.read())

                self._posts_per_month[key] = posts

        return self._posts_per_month[key]

    def get_posts_by_year(self, year):
        posts = []
        for month in range(1, 13):
            posts += self.get_posts_by_year_month(year, month)
        return posts

    def get_post(self, year, month, day, day_index):
        posts = self.get_posts_by_year_month(year, month)
        for p in posts:
            if p["date"].day == day and p["day_index"] == day_index:
                return p
        return None

    def get_post_by_key(self, key):
        date = datetime.datetime.strptime(key[:10], "%Y-%m-%d")
        day_index = int(key[11:])
        return self.get_post(date.year, date.month, date.day, day_index)

    def get_all_posts(self):
        posts = []
        for year in range(2005, datetime.date.today().year+1):
            for month in range(1, 13):
                if year == 2005 and month < 3:
                    continue
                posts += self.get_posts_by_year_month(year, month)
        return posts

    def get_random_post(self, year=None, month=None, day=None):
        num_tries = 0
        posts = None
        while num_tries < 100:
            ryear = year or random.randrange(2005, datetime.date.today().year+1)
            rmonth = month or random.randrange(3 if year==2005 else 1, 13)
            posts = self.get_posts_by_year_month(ryear, rmonth)
            if day:
                if posts:
                    posts = [p for p in posts if p["date"].day == day]
                if not posts:
                    return None
            if posts:
                break
            num_tries += 1
        return None if not posts else posts[random.randrange(len(posts))]

    def render_post_to_discord(self, post):
        # print(post)

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
                inserts.append([start, "\n```\n"])
                inserts.append([end, "```\n"])
            elif name == "li":
                inserts.append([start, "\n- "])

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

        markup = "`%s #%s`\n%s\n%s" % (post["date"], post["day_index"], markup, links)

        return markup

    def is_search_ready(self):
        return self._corpus and self._corpus.is_ready()

    def search_posts(self, query):
        if self._corpus is None:
            from threading import Thread
            self._corpus = CorpusIndex()
            Thread(target=self._build_index).start()

        if not self.is_search_ready():
            return None

        query = query.lower()
        weighted_doc_ids = self._corpus.weighted_document_ids_for_tokens_AND(query.split())
        if not weighted_doc_ids:
            return None

        if 0:
            print(", ".join("%s: %s" % (id, weighted_doc_ids[id])
                            for id in sorted(weighted_doc_ids, key=lambda x: weighted_doc_ids[x])))
        return [
            self.get_post_by_key(key)
            for key in sorted(weighted_doc_ids, key=lambda k: -weighted_doc_ids[k])
        ]