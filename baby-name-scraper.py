import sys
import json
import requests

from lxml import html
from datetime import datetime

if len(sys.argv) > 1:
	category = sys.argv[1]
	url = f'https://adoption.com/baby-names/origin/{category}?page={{page}}'
else:
	url = 'https://adoption.com/baby-names/browse?page={page}'

r = requests.get(url.format(page=1))
h = html.document_fromstring(r.text)

# find max page
max_page = int(h.xpath('//body/div/main/div[4]/div[2]/div/ul/li')[-2].text_content())
page_iter = 1
data: list[dict] = list()
while page_iter <= max_page:
	r = requests.get(url.format(page=page_iter))
	h = html.document_fromstring(r.text)
	rows = h.xpath('//body/div/main/div[4]/div[2]/div/table/tbody/tr')
	for row in rows:
		row = list(map(lambda x: x.text_content(), row.xpath('./td')))
		if len(row) < 4:
			continue
		data.append({
			"name": row[0],
			"meaning": row[1],
			"gender": row[2],
			"origin": row[3]	
		})
	page_iter += 1

fname = datetime.now().strftime('%y-%m-%d-%H-%M')
with open(f'/tmp/{fname}.json', 'w') as file:
	json.dump(data, file)
