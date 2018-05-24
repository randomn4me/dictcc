#!/usr/bin/python

import sys
import requests
from bs4 import BeautifulSoup

def usage(argv):
    sys.stderr.write("Usage: %s <word>\n".format(argv[0]))
    sys.exit(1)

def request(word):
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0'}
    payload = {'s': word}

    try:
        r = requests.get(
                "https://ende.dict.cc/",
                headers=header,
                params=payload)
    except Exception as exeption:
        print(e)
        sys.exit(1)

    return r.content

def parse_single_tag(tag):
    str_tag = " ".join([a_tag.text for a_tag in tag.find_all('a')])
    if (tag.dfn):
        all_dfn = ", ".join([dfn_tag.text for dfn_tag in tag.find_all('dfn')])
        str_tag = ' '.join([str_tag, '(' + all_dfn + ')'])

    return str_tag


def parse_all(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = [tag for tag in soup.find_all('td', 'td7nl')]

    raw_from_to = zip(data[::2], data[1::2])
    res_from_to = list()

    for f, t in raw_from_to:
        res_from_to.append((parse_single_tag(f), parse_single_tag(t)))

    return res_from_to

def main(argv):
    if not len(argv) == 2:
        usage(argv)

    c = request(argv[1])
    data = parse_all(c)

    for pair in data:
        print("{0[0]}\t==\t{0[1]}".format(pair))

    if not data:
        print(' '.join(["No translation found for:", argv[1]]))

    return 0

if __name__ == '__main__':
    main(sys.argv)
