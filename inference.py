import csv, os
from inference import gpt4, llamaguard, llama2, mixtral
from utils import Prefs, xlstocsv
from utils import translator
from concurrent.futures import ThreadPoolExecutor
from itertools import islice


headers = {}
headers['gpt4'] = ['gpt4 offensive', 'gpt4 major reasons', 'gpt4 minor reasons', 'gpt4 time']
headers['llama2'] = ['llama2 offensive', 'llama2 reasons', 'llama2 time']
headers['mixtral'] = ['mixtral offensive', 'mixtral reasons', 'mixtral time']
headers['llamaguard'] = ['llamaguard offensive', 'llamaguard reasons', 'llamaguard time']

file = Prefs().getPref('inputfile', 'csv')
llm = Prefs().getPref('llm')
workers = 1
if llm != "gpt4":
    workers = 8
    

# Convert XLSX to CSV
if file.endswith("xlsx") or file.endswith("xls"):
    file = xlstocsv(file)

# Read CSV and run inference
translate = False
with open(os.path.join('csv', file), newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    results = []
    header = []
    header.extend(reader.fieldnames)
    if 'translated' not in header:
        header.append('translated')
        translate = True
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for batch in iter(lambda: list(islice(reader, workers)), []):
                futures = [executor.submit(translator.Translator().translate, row) for row in batch]
                results += [future.result() for future in futures]

# Write output CSV
if translate == True:
    with open(os.path.join('csv', file), 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=header, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


with open(os.path.join('csv', file), newline='') as csvfile:    
    reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    results = []
    header = []
    header.extend(reader.fieldnames)
    header.extend(headers[llm])
    results = []
    if llm == "llamaguard":
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for batch in iter(lambda: list(islice(reader, workers)), []):
                futures = [executor.submit(llamaguard.Query(), row) for row in batch]
                results += [future.result() for future in futures]
    elif llm == "llama2":
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for batch in iter(lambda: list(islice(reader, workers)), []):
                futures = [executor.submit(llama2.Query(), row) for row in batch]
                results += [future.result() for future in futures]
    elif llm == "mixtral":
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for batch in iter(lambda: list(islice(reader, workers)), []):
                futures = [executor.submit(mixtral.Query(), row) for row in batch]
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
        try:
            writer.writerow(row)
        except Exception as e:
            pass
