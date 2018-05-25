#!/usr/bin/python
import sys
import requests
import argparse
from bs4 import BeautifulSoup

def request(word, f, t):
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0'}
    payload = {'s': word}

    try:
        r = requests.get(
                "https://{}{}.dict.cc/".format(f, t),
                headers=header,
                params=payload)
    except Exception as exeption:
        print(e)
        exit(1)

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

def main(args):
    c = request(args.word, args.prim, args.sec)
    data = parse_all(c)

    for pair in data:
        print("{0[0]}\t==\t{0[1]}".format(pair))

    if not data:
        print(' '.join(["No translation found for:", args.word]))

    return 0

if __name__ == '__main__':
    prim = ['de', 'en']
    sec = ['bg', 'bs', 'cs', 'da', 'el', 'eo', 'es', 'fi', 'fr', 'hr',
            'hu', 'is', 'it', 'la', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk',
            'sq', 'sr', 'sv', 'tr']
    all_dict = prim + sec
    parser = argparse.ArgumentParser(description='Query dict.cc for a translation.')
    parser.add_argument('-p', '--prim', type=str, default='en', help='Primary language')
    parser.add_argument('-s', '--sec', type=str, default='de', help='Secondary language')
    parser.add_argument('word', type=str, help='word to translate')

    args = parser.parse_args()

    if not args.prim in prim:
        print("Primary lang must be in : [" + ", ".join(prim) + "]")
        exit(1)
    if not args.sec in all_dict:
        print("Secondary lang must be in : [" + ", ".join(all_dict) + "]")
        exit(1)
    if args.prim == args.sec:
        print("Languages must be different. Given : \"{}\" \"{}\"".format(args.prim, args.sec))
        exit(1)

    main(args)
