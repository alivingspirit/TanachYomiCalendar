import re
import bs4
import gematriapy
from collections import namedtuple
import pprint
import io
import calendar
from datetime import date, timedelta
from pyluach import dates, hebrewcal, parshios

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


Pasuk = namedtuple('Pasuk', 'book,perek,num_of_pasukim')


def expand_range():
    for book, perek_count in all_counts:
        for perek, num_of_pesukim in perek_count:
            yield Pasuk(book, perek, num_of_pesukim)



Day = namedtuple('Day', 'num,sections,gregorian_day,hebrew_day,num_of_pasukim')

average_target = 8.215787532275913
def get_days():
    pasukim_processed = 0;
    running_average = 0
    current_date = date.fromisoformat('2020-01-05') - timedelta(1)
    expanded = list(expand_range())
    day = 0
    for book, perek, num_of_pesukim in expanded:
        days_to_read = num_of_pesukim // 8
        leftover_pasukim = num_of_pesukim % 8
        if (leftover_pasukim and running_average > average_target) or days_to_read == 0:
            days_to_read += 1

        distribution = [num_of_pesukim // days_to_read] * days_to_read
        for i, _ in enumerate(range(num_of_pesukim % days_to_read)):
            distribution[i % len(distribution)] += 1

        first = 1
        for i, num_of_pesukim_today in enumerate(distribution):
            day += 1
            is_last = i == len(distribution) - 1
            current_date += timedelta(1)
            hebrew_day = dates.GregorianDate.from_pydate(current_date).to_heb()
            last = first + num_of_pesukim_today
            first_gematria = gematriapy.to_hebrew(first)
            last_gematria = gematriapy.to_hebrew(last) # if is_last else gematriapy.to_hebrew(last)
            sections = f'{book} {gematriapy.to_hebrew(perek)} {first_gematria}-{last_gematria}'
            yield Day(day,
                      sections,
                      current_date.strftime('%Y-%m-%d'),
                      hebrew_day.hebrew_date_string(),
                      num_of_pesukim_today)._asdict()
            first = last
        pasukim_processed += num_of_pesukim
        running_average = pasukim_processed / day

if __name__ == '__main__':
    import json
    with open('calculation.json', 'w') as file:
        file.write(json.dumps(list(get_days())))