import csv, os
from query import Query
from utils import Prefs
from utils import xlstocsv
from concurrent.futures import ThreadPoolExecutor
from itertools import islice


file = Prefs().getPref('csv', 'file')
llm = Prefs().getPref('llm', 'llm')
workers = 1
if llm != "gpt4":
    workers = 2

if file.endswith("xlsx") or file.endswith("xls"):
    file = xlstocsv(file)

with open(os.path.join('csv', file), newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    results = []
    header = reader.fieldnames
    header.append('offensive')
    header.append('reasons')
    header.append('time')
    
    if llm == "gpt4":
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for batch in iter(lambda: list(islice(reader, workers)), []):
                futures = [executor.submit(Query.gptScore, row) for row in batch]
                results += [future.result() for future in futures]
    elif llm == "llama2":
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for batch in iter(lambda: list(islice(reader, workers)), []):
                futures = [executor.submit(Query.llamaScore, row) for row in batch]
                results += [future.result() for future in futures]

outfile = 'output_' + file
with open(os.path.join('csv', outfile), 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in results:
        writer.writerow(row)
