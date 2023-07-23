import re
import bs4
import gematriapy
from collections import namedtuple
import pprint
import io

pp = pprint.PrettyPrinter(indent=4)

texts_path = ".\\k001\\k\\"

books = [
    ("תורה", "k01.htm", "בראשית", ''),
    ("תורה", "k02.htm", "שמות", ''),
    ("תורה", "k03.htm", "ויקרא", ''),
    ("תורה", "k04.htm", "במדבר", ''),
    ("תורה", "k05.htm", "דברים", ''),
    ("נביאים", "k06.htm", "יהושוע", ''),
    ("נביאים", "k07.htm", "שופטים", ''),
    ("נביאים", "k08.htm", "שמואל א", 'א'),
    ("נביאים", "k08.htm", "שמואל ב", 'ב'),
    ("נביאים", "k09.htm", "מלכים א", 'א'),
    ("נביאים", "k09.htm", "מלכים ב", 'ב'),
    ("נביאים", "k10.htm", "ישעיהו", ''),
    ("נביאים", "k11.htm", "ירמיהו", ''),
    ("נביאים", "k12.htm", "יחזקאל", ''),
    ("נביאים", "k13.htm", "הושע", ''),
    ("נביאים", "k14.htm", "יואל", ''),
    ("נביאים", "k15.htm", "עמוס", ''),
    ("נביאים", "k16.htm", "עובדיה", ''),
    ("נביאים", "k17.htm", "יונה", ''),
    ("נביאים", "k18.htm", "מיכה", ''),
    ("נביאים", "k19.htm", "נחום", ''),
    ("נביאים", "k20.htm", "חבקוק", ''),
    ("נביאים", "k21.htm", "צפניה", ''),
    ("נביאים", "k22.htm", "חגיי", ''),
    ("נביאים", "k23.htm", "זכריה", ''),
    ("נביאים", "k24.htm", "מלאכי", ''),
    ("כתובים", "k25.htm", "דברי הימים א", 'א'),
    ("כתובים", "k25.htm", "דברי הימים ב", 'ב'),
    ("כתובים", "k26.htm", "תהילים", ''),
    ("כתובים", "k27.htm", "איוב", ''),
    ("כתובים", "k28.htm", "משלי", ''),
    ("כתובים", "k29.htm", "רות", ''),
    ("כתובים", "k30.htm", "שיר השירים", ''),
    ("כתובים", "k31.htm", "קוהלת", ''),
    ("כתובים", "k32.htm", "איכה", ''),
    ("כתובים", "k33.htm", "אסתר", ''),
    ("כתובים", "k34.htm", "דנייאל", ''),
    ("כתובים", "k35.htm", "עזרא", "ע"),
    ("כתובים", "k35.htm", "נחמיה", 'נ')
]

def read_file_text(file_name):
    with io.open(texts_path + file_name, mode='r', encoding='ISO-8859-8') as file:
        return file.read()

book_text = [(part,book,read_file_text(html_file),match) for part,html_file,book,match in books]

from itertools import groupby, starmap
from operator import itemgetter
def get_perakim_counts(part,book,filetext,match):
    pesukim = re.findall(r'<b>(?:(?P<part>[^\u00A0,]*?)[\u00A0])?(?P<perek>[^\u00A0,]*?),(?P<pasuk>[^<]*?)</b>', filetext, re.MULTILINE | re.IGNORECASE)
    matching_pasukim = [(perek,pasuk)
                        for part,perek,pasuk in pesukim
                        if part == match]
    numeric_pasukim = [(gematriapy.to_number(perek), gematriapy.to_number(pasuk)) for perek, pasuk in matching_pasukim]
    perek_count = [(perek,max(map(itemgetter(1),group)) - 1)
                   for perek, group in groupby(numeric_pasukim, itemgetter(0))]
    return book, perek_count

all_counts = starmap(get_perakim_counts, book_text)

pesukim_per_day = 9

Pasuk = namedtuple('Pasuk', 'book,perek,pasuk')


def expand_range():
    for book, perek_count in all_counts:
        for perek, num_of_pesukim in perek_count:
            for pasuk in range(num_of_pesukim):
                yield Pasuk(book, perek, pasuk)

file_head = '''
<html dir="RTL" lang="HE">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=Windows-1255">
        <style>
            body {font-family:David;color:#000000;background-color:#FFFFFF;margin:1.5em;}
            p {font-size:165%;text-align:justify;}
            p.r {font-size:165%;text-align:right;}
            p.m {font-size:120%;text-align:justify;}
            p.s {font-size:100%;text-align:justify;}
            tr {font-size:135%;}
            h1 {font-size:260%;}
            h2 {font-size:210%;}
            h3 {font-size:180%;}
            big {font-size:120%;vertical-align:-7%;}
            b {font-size:70%;vertical-align:9%;}
            small {font-size:80%;vertical-align:12%;font-weight:bold}
            sup {font-size:115%;vertical-align:15%;}
            span.tiny {font-size:80%;}
            span.x {color:#660066;}
            span.y {font-size:80%;}
            span.eng {font-family:"Times New Roman, Arial";font-size:80%;}
            table {
              border-collapse: collapse;
            }
            th, td {
              border: 1px solid black;
            }
        </style>
    </head>
    <body>
        <table>
            <tr><th>Day</th><th>Pasukim</th></tr>
'''

file_tail = '''
        </table>
    </body>
</html>
'''
expanded = list(expand_range())
with io.open("./results.html", mode='w', encoding='utf-8') as resultsfile:
    resultsfile.write(file_head)
    for day in range(len(expanded) // pesukim_per_day):
        resultsfile.write(f'<tr><td>{day + 1}</td><td>')
        grouped = groupby(expanded[day * pesukim_per_day: (day + 1) * pesukim_per_day],
                          lambda p: p.book + ': ' + gematriapy.to_hebrew(p.perek))
        for book_perek, pesukim in grouped:
            pesukim_numbers = list(map(itemgetter(2), pesukim))
            first, last = min(pesukim_numbers) + 1, max(pesukim_numbers) + 1
            resultsfile.write(f'<div>{book_perek} {gematriapy.to_hebrew(first)}-{gematriapy.to_hebrew(last)}</div>')
        resultsfile.write('</td></tr> \n')
    resultsfile.write(file_tail)
