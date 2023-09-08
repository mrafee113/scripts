import sys
import requests

from lxml import html
from urllib.parse import urlsplit

if len(sys.argv) < 2:
    print("not enough arguments..")
    exit(1)

url = sys.argv[1]
s = urlsplit(url)
r = requests.get(url)
tree = html.document_fromstring(r.text)
viable_elements = tree.xpath('//body//a[@href]')
links = list()
for el in viable_elements:
    try:
        links.append(s.scheme + '://' + s.hostname + s.path + str(el.attrib['href']))
    except Exception as exc:
        pass

with open("/tmp/links.txt", 'w') as file:
    file.write('\n'.join(links))

exit(0)
