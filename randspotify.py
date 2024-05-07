import csv
import random
from prettytable import PrettyTable
from termcolor import colored

file_path = '/home/francis/Bedroom/Documents/spotify-playlists/all.csv'

with open(file_path, newline="") as file:
    reader = csv.DictReader(file)
    data = list(reader)

random_line = random.choice(data)
random_line['Duration (ms)'] = str(round(float(random_line['Duration (ms)']) / 60000, 2))

columns = ["Track Name", "Album Name", "Artist Name(s)", "Release Date", "Duration (ms)", "Genres"]
table = PrettyTable(columns)
table.field_names = columns
table.add_row([random_line[column] for column in columns])
colored_headers = [colored(header, 'red') for header in table.field_names]
table.field_names = colored_headers
print(table)
