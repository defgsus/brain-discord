# coding=utf-8
import requests
from xml.etree import ElementTree as ET

from .credentials import ACCESS_TOKEN

__all__ = ("make_query", "query_author")


def query_author(name_part):
    query = 'per all "%s" and mat=persons' % name_part
    return make_query(query, category="authorities", format="RDFxml")


def make_query(query_str, category="authorities", format="RDFxml"):
    """
    :param query_str: Search string as described here: http://www.dnb.de/DE/Service/DigitaleDienste/SRU/sru_node.html#Aufbau
    :param category: authorities, dnb, dnb.dma (http://www.dnb.de/DE/Service/DigitaleDienste/SRU/sru_node.html#doc208430bodyText3)
    :param format: MARC21-xml, RDFxml (http://www.dnb.de/DE/Service/DigitaleDienste/SRU/sru_node.html#doc208430bodyText4)
    """
    url = "https://services.dnb.de/sru/%s" % category
    try:
        res = requests.get(url, {
            "version": "1.1",
            "accessToken": ACCESS_TOKEN,
            "operation": "searchRetrieve",
            "recordSchema": format,
            "query": query_str
        }, timeout=2.)
    except requests.RequestException:
        return []
    #print(res.url)
    #print(res.content)
    #with open("./test.xml", b"w") as f:
    #    f.write(res.content)
    root = parse_xml(res.content)
    #print(root)
    return parse_records(root)


def parse_xml(text):
    """Returns the ElementTree root node.
    Removes all namespaces from the elements' tags"""
    root = ET.fromstring(text)
    for el in root.iter():
        if '}' in el.tag:
            el.tag = el.tag.split('}', 1)[-1]
    return root


def parse_records(root):
    entries = []
    records = root.findall("*//recordData")
    for rec in records:
        entry = record_to_dict(rec)
        entries.append(entry)
    return entries


def record_to_dict(rec_node, dic=None):
    if dic is None:
        dic = dict()
    for c in rec_node.getchildren():
        if c.text:
            text = c.text.strip()
            if text:
                tag = c.tag.split("}")[-1]
                if tag not in dic:
                    dic[tag] = text
                else:
                    if isinstance(dic[tag], list):
                        if not text in dic[tag]:
                            dic[tag].append(text)
                    else:
                        if text != dic[tag]:
                            dic[tag] = [dic[tag], text]
        record_to_dict(c, dic)
    return dic


def dump_entries(entries):
    for e in entries:
        print("-----")
        for key in sorted(e):
            print("%40s : %s" % (key, e[key]))

