import re
import time

from urllib.request import urlopen
import bs4


def get_genres(soup):
    genres = []
    for node in soup.find_all('div', {'class': 'left'}):
        current_genres = node.find_all('a', {'class': 'actionLinkLite bookPageGenreLink'})
        current_genres = [g.text for g in current_genres]
        if len(current_genres) >= 1:
            genres.extend(current_genres)
    return list(set(genres))

def get_num_pages(soup):
    if soup.find('span', {'itemprop': 'numberOfPages'}):
        num_pages = soup.find('span', {'itemprop': 'numberOfPages'}).text.strip()
        return int(num_pages.split()[0])
    return ''


def get_year_first_published(soup):
    year_first_published = soup.find('nobr', attrs={'class':'greyText'})
    if year_first_published:
        year_first_published = year_first_published.string
        return re.search('([0-9]{3,4})', year_first_published).group(1)
    else:
        return ''

def scrape_book(url):
    source = urlopen(url)
    soup = bs4.BeautifulSoup(source, 'html.parser')

    time.sleep(2)

    return {'book_title':           ' '.join(soup.find('h1', {'id': 'bookTitle'}).text.split()),
            'year_first_published': get_year_first_published(soup),
            'author':               ' '.join(soup.find('span', {'itemprop': 'name'}).text.split()),
            'num_pages':            get_num_pages(soup),
            'genres':               get_genres(soup),
            'num_ratings':          soup.find('meta', {'itemprop': 'ratingCount'})['content'].strip(),
            'num_reviews':          soup.find('meta', {'itemprop': 'reviewCount'})['content'].strip(),
            'average_rating':       soup.find('span', {'itemprop': 'ratingValue'}).text.strip()}


