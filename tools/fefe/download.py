import os
import time
import datetime
import requests


DEFAULT_HTML_CACHE_DIR = "./fefe-html-cache"
USER_AGENT = "Hallo Fefe! Python/requests"


def download_fefe(year, month,
                  cache_dir=DEFAULT_HTML_CACHE_DIR,
                  skip_when_cached=True,
                  session=None):
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    if session is None:
        session = requests.session()
        session.headers["User-Agent"] = USER_AGENT

    filename = os.path.join(cache_dir, "{:04d}-{:02d}.html".format(year, month))
    if skip_when_cached and os.path.exists(filename):
        return filename

    url = "http://blog.fefe.de/?mon={:04d}{:02d}".format(year, month)
    print("downloading %s" % url)

    res = session.get(url)

    with open(filename, "w") as fp:
        fp.write(res.content.decode("utf-8"))

    return filename


def download_fefe_range(mindate=None, maxdate=None,
                        cache_dir=DEFAULT_HTML_CACHE_DIR,
                        skip_when_cached=True):

    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    ses = requests.session()
    ses.headers["User-Agent"] = USER_AGENT

    mindate = mindate or datetime.date(2005, 3, 1)
    maxdate = maxdate or datetime.date.today()
    for year in range(mindate.year, maxdate.year+1):
        for month in range(1, 13):
            if year == mindate.year and month < mindate.month:
                continue
            if year == maxdate.year and month > maxdate.month:
                continue

            download_fefe(year, month, skip_when_cached=skip_when_cached, session=ses)

            time.sleep(.5)
