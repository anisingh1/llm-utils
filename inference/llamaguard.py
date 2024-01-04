from utils import Prefs
from dotenv import load_dotenv
from dotenv import dotenv_values
import time, json
import requests

load_dotenv()
secrets = dotenv_values(".env")

tags = {
    "01": "Violence and Hate",
    "02": "Sexual Content",
    "03": "Criminal Planning",
    "04": "Guns and Illegal Weapons",
    "05": "Regulated or Controlled Substances",
    "06": "Self-Harm"
}
class _query:
    inputcolumn = None
    llm = None
    endpoint = None
    header = {}
    chat = None

    def __init__(self):
        self.inputcolumn = Prefs().getPref('inputcolumn', 'csv')
        self.region = Prefs().getPref('region')
        self.llm = Prefs().getPref('llm')
        self.endpoint = Prefs().getPref('url', self.llm)


    def ask(self, row):
        try:
            reqUrl = self.endpoint + "?text=" + row[self.inputcolumn]
            start = time.time()
            x = requests.post(reqUrl, timeout=30)
            end = time.time()
            x = x.text.strip("\"")

            print("OUTPUT: " + row[self.inputcolumn] + " : " + x)
            row[self.llm + ' time'] = round(end - start, 2)
            x = x.split('\\n')
            if x[0].startswith('safe'):
                row[self.llm + ' reasons'] = ""
                row[self.llm + ' offensive'] = False
            elif x[0].startswith('unsafe'):
                row[self.llm + ' offensive'] = True
                row[self.llm + ' reasons'] = ""
                if len(x) > 1:
                    x[1] = x[1].strip(" ")
                    if tags[x[1]] != None:
                        row[self.llm + ' reasons'] = tags[x[1]]
            return row
        except Exception as e:
            print(e)
            row[self.llm + ' offensive'] = 'error'
            row[self.llm + ' reasons'] = e
            return row


_queryObj = _query()
def Query(): return _queryObj.ask()
