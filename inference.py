import csv, os
from inference import gpt4, llamaguard
from utils import Prefs
from utils import xlstocsv
from concurrent.futures import ThreadPoolExecutor
from itertools import islice


file = Prefs().getPref('inputfile', 'csv')
llm = Prefs().getPref('llm')
workers = 1
if llm != "gpt4":
    workers = 2

# Convert XLSX to CSV
if file.endswith("xlsx") or file.endswith("xls"):
    file = xlstocsv(file)

# Read CSV and run inference
with open(os.path.join('csv', file), newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    results = []
    header = reader.fieldnames
    header.append(llm + ' offensive')
    header.append(llm + ' reasons')
    header.append(llm + ' time')
    
    if llm == "llama2_7b_guard":
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for batch in iter(lambda: list(islice(reader, workers)), []):
                futures = [executor.submit(llamaguard.Query(), row) for row in batch]
                results += [future.result() for future in futures]
    elif llm == "gpt4":
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for batch in iter(lambda: list(islice(reader, workers)), []):
                futures = [executor.submit(gpt4.Query(), row) for row in batch]
                results += [future.result() for future in futures]

# Write output CSV
outfile = 'output_' + file
with open(os.path.join('csv', outfile), 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in results:
        writer.writerow(row)
