import datetime
from bs4 import BeautifulSoup
from xml.etree import ElementTree as ET
from html.parser import HTMLParser


MONTH_NAMES = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

AUTO_CLOSE_TAGS = {
    "ul": ["ul", "li", "p", "b", "blockquote"],
    "li": ["li", "p", "b", "blockquote"],
    "p": ["p"],
    "blockquote": ["blockquote", "p"],
}


def _fefe_date_str_to_date(s):
    s = s.split()
    return datetime.datetime(int(s[-1]), MONTH_NAMES.index(s[-3])+1, int(s[-2]), 0, 0, 0)


def dump_post(post):
    print(post)
    for tag in post["tags"]:
        print(tag["tag"], "[%s]" % post["text"][tag["i"][0]:tag["i"][1]], tag.get("url", ""))


class PostParser(HTMLParser):

    def __init__(self, *args, **kwargs):
        super(PostParser, self).__init__(*args, **kwargs)
        self.tags = []
        self.cur_href = None
        self.day_index = None
        self.post = {
            "text": "",
            "tags": [],
        }

    def tag(self):
        return self.tags[-1] if self.tags else ""

    def push_tag(self, tag):
        self.tags.append(tag)

    def pop_tag(self):
        if self.tags:
            self.tags.pop()

    def inside_tag(self, tag):
        for t in reversed(self.tags):
            if t == tag:
                return True
        return False

    def tag_count(self, tag):
        return sum(1 for t in self.tags if t == tag)

    def handle_starttag(self, tag, attrs):
        #print("starttag", tag, self.tags)
        #if not self.post["text"].endswith(" "):
        #    self.post["text"] += " "

        if tag == "a":
            attrs = {t[0]: t[1] for t in attrs}
            self.cur_href = attrs.get("href")

        for auto_close in AUTO_CLOSE_TAGS:
            if tag == auto_close:
                options = AUTO_CLOSE_TAGS[tag]
                while self.tag() in options:
                    self.handle_endtag(self.tag())
        if tag == "p" or tag == "br":
            if self.post:
                self.post["text"] += "\n"
            return

        #print("OPEN", tag, self.tags)
        self.push_tag(tag)

    def handle_endtag(self, tag):
        #print("CLOSE", tag, self.tags)
        if self.tags:
            if self.tags[-1] == tag:
                self.pop_tag()
            else:
                while True:
                    if self.tags[-1] in AUTO_CLOSE_TAGS.get(tag, []):
                        prevtag = self.tags[-1]
                        self.pop_tag()
                        if not self.tags or prevtag == tag:
                            break
                    else:
                        self.pop_tag()
                        break
            if not self.post["text"].endswith(" "):
                self.post["text"] += " "

    def handle_data(self, data):
        start_space = data.startswith(" ")
        end_space = data.endswith(" ")
        if start_space and self.post["text"] and not self.post["text"].endswith(" "):
            self.post["text"] += " "
        start = len(self.post["text"])
        self.post["text"] += data.replace("\n", " ").replace("  ", " ").strip()
        if end_space:
            self.post["text"] += " "
        end = len(self.post["text"])

        if self.tag():
            e = {"tag":self.tag(), "i": [start, end]}
            if self.tag() == "a" and self.cur_href:
                e["url"] = self.cur_href

            #if self.enclosing_tags:
            #    self.enclosing_tags[-1]["i"][1] = e["i"][1]
            #else:
            #    if e["tag"] in ENCLOSING_TAGS:
            #        self.enclosing_tags.append(e)

            for other in self.post["tags"]:
                if other["tag"] == e["tag"]:
                    if other["i"][0] <= e["i"][0] and other["i"][1] >= e["i"][1]:
                        other["i"][1] = e["i"][1]
                        e = None
                        break
            if e:
                self.post["tags"].append(e)


def parse_blog_html(markup, database=None):
    import re

    days = []
    for match in re.finditer(r'<h3>(.+)</h3>', markup):
        days.append((match.span()[0], _fefe_date_str_to_date(match.groups()[0])))

    ret_posts = []
    for i in range(len(days)):
        if i < len(days)-1:
            markup_part = markup[days[i][0]:days[i+1][0]]
        else:
            markup_part = markup[days[i][0]:]
        #print(days[i][1])
        posts_markup = []
        for match in re.findall(r'<a href="(\?ts=[0-9a-z]+)">\[l\]</a>(.+)', markup_part):
            url = match[0]
            post_markup = match[1][1:]
            posts_markup.append((url, post_markup))

        for j, post_markup in enumerate(posts_markup):
            p = PostParser()
            p.feed(post_markup[1])
            post = p.post
            post["text"] = post["text"].strip()
            post["date"] = days[i][1].date()
            post["url"] = "http://blog.fefe.de%s" % post_markup[0]
            post["day_index"] = len(posts_markup)-1-j

            ret_posts.append(post)
            #dump_post(post)

    return ret_posts
