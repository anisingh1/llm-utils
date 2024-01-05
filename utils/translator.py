import json
import requests
from utils import Prefs
from dotenv import load_dotenv, dotenv_values

load_dotenv()
secrets = dotenv_values(".env")

class _translate:
    inputcolumn = None
    endpoint = None
    header = {}

    def __init__(self):
        self.inputcolumn = Prefs().getPref('inputcolumn', 'csv')
        self.endpoint = Prefs().getPref('url', 'azure')
        self.header = {
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': secrets['azurekey'],
            'Ocp-Apim-Subscription-Region': 'eastus'
        }


    def translate(self, row):
        try:
            targetlanguage = 'en'
            reqUrl = self.endpoint + '/translator/text/v3.0/translate?to=' + targetlanguage
            body = [{
                'Text': row[self.inputcolumn]
            }]
            x = requests.post(reqUrl, data=json.dumps(body), headers=self.header, timeout=30)
            x = json.loads(x.text)[0]
            row['translated'] = x['translations'][0]['text']
            return row
        except Exception as e:
            print(e)
            return row


_translateObj = _translate()
def Translator(): return _translateObj