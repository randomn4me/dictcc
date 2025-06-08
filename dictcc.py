#!/usr/bin/python3

import sys
import requests
import argparse
import os
import textwrap

from tabulate import tabulate
from bs4 import BeautifulSoup

_, columns = os.popen('stty size', 'r').read().split()

requests_session = requests.Session()

def request(word, f, t):
    header = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0'}
    payload = {'s': word}

    try:
        r = requests_session.get(
                "https://{}{}.dict.cc/".format(f, t),
                headers=header,
                params=payload)
    except Exception as e:
        print(e)
        exit(1)

    return r.content

def parse_single_tag(tag):
    str_tag = " ".join([a_tag.text for a_tag in tag.find_all('a')])
    if (tag.dfn):
        all_dfn = ", ".join([dfn_tag.text for dfn_tag in tag.find_all('dfn')])
        str_tag = ' '.join([str_tag, '(' + all_dfn + ')'])

    return '\n   '.join(textwrap.wrap(str_tag, (int(columns) - 8) // 2))

def parse_response(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = [tag for tag in soup.find_all('td', 'td7nl')]
    displayed_results = args.max if (args.max < len(data)//2 ) else len(data)//2

    raw_from_to = zip(data[:displayed_results*2:2], data[1:displayed_results*2:2])
    res_from_to = list()

    for f, t in raw_from_to:
        res_from_to.append([parse_single_tag(f), parse_single_tag(t)])

    return res_from_to

def parse_suggestions(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = [tag.a.text for tag in soup.find_all('td', 'td3nl') if tag.a]

    return data

def handle_translation(word, primary_lang, secondary_lang):
    c = request(word, primary_lang, secondary_lang)
    data = parse_response(c)

    if data:
        print(tabulate(data, [primary_lang, secondary_lang], tablefmt='orgtbl'))
    else:
        print(' '.join(["No translation found for:", word]))
        suggestions = parse_suggestions(c)
        print('\nHere are suggestions given by dict.cc:')
        for s in suggestions:
            print(" - {}".format(s))

def main(args):
    if not args.console and args.word:
        handle_translation(args.word[0], args.prim, args.sec)
    elif args.console:
        print('Starting console')
        print('Enter your words for translation')
        print('Enter q for exit')

        user_input = input('>> ')
        while user_input != 'q':
            handle_translation(user_input, args.prim, args.sec)
            user_input = input('>> ')

if __name__ == '__main__':
    prim = ['de', 'en']
    sec = ['bg', 'bs', 'cs', 'da', 'el', 'eo', 'es', 'fi', 'fr', 'hr',
            'hu', 'is', 'it', 'la', 'nl', 'no', 'pl', 'pt', 'ro', 'ru', 'sk',
            'sq', 'sr', 'sv', 'tr']
    all_dict = prim + sec
    parser = argparse.ArgumentParser(
            description='Query dict.cc for a translation.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p', '--prim', type=str, default='en', help='Primary language')
    parser.add_argument('-s', '--sec', type=str, default='de', help='Secondary language')
    parser.add_argument('-c', '--console', action='store_true')
    parser.add_argument('-m', '--max', type=int, default=10, help='max number of results to show')
    parser.add_argument('word', nargs=argparse.REMAINDER, help='word to translate')

    args = parser.parse_args()

    if not args.prim in prim:
        print("Primary lang must be in : [" + ", ".join(prim) + "]")
        exit(1)
    if not args.sec in all_dict:
        print("Secondary lang must be in : [" + ", ".join(all_dict) + "]")
        exit(1)
    if args.prim == args.sec:
        print("Given languages must be different. Given : \"{}\" and \"{}\"".format(args.prim, args.sec))
        exit(1)
    if not (args.max > 0):
        print("maximum number of results must be greater than 0")
        exit(1)

    main(args)
