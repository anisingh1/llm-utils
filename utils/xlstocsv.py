import xlrd
import csv
from pathlib import Path


def xlstocsv(file, sheet="Sheet1"):
    wb = xlrd.open_workbook(file)
    sh = wb.sheet_by_name(sheet)
    outfile = Path(file).stem + ".csv"
    csvFile = open(outfile, 'wb')
    wr = csv.writer(csvFile, quoting=csv.QUOTE_ALL)

    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    csvFile.close()
    return outfile