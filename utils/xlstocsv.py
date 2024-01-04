import xlrd
import os
import csv
from pathlib import Path


def xlstocsv(file, sheet="Sheet1"):
    file = os.path.join('csv', file)
    wb = xlrd.open_workbook(file)
    sh = wb.sheet_by_name(sheet)
    outfile = Path(file).stem + ".csv"
    csvFile = open(os.path.join('csv', outfile), 'w', encoding="utf-8")
    wr = csv.writer(csvFile, quoting=csv.QUOTE_MINIMAL)

    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    csvFile.close()
    return outfile