import requests, json, time
from utils import Prefs
from dotenv import load_dotenv
from dotenv import dotenv_values

load_dotenv()
secrets = dotenv_values(".env")

class _Query:
    inputcolumn = None

    def __init__(self):
        self.inputcolumn = Prefs().getPref('inputcolumn', 'csv')
        self.region = Prefs().getPref('region', 'llm')


    def message(self, row):
        context = "Provide a list of reasons with each reason described in around 10 words in JSON format along with their severity (categorized as High, Medium, and Low) for the user-provided text input to be culturally offensive to the majority of people in " + self.region + ". Don't make any presumptions and only consider the user-provided text input for evaluation. Merge similar reasons together and provide the response within 150 words. The complete response should be a valid JSON."
        conversation = [
            {
                "role":"system",
                "content":context
            },
            {
                "role":"user",
                "content":"Jesus Christ as a general of an Army"
            },
            {
                "role":"assistant",
                "content":"[{\"reason\": \"Disrespecting religious sentiments of Christians\",\"severity\": \"High\"},{\"reason\": \"Misrepresentation of Jesus' peaceful teachings\",\"severity\": \"High\"},{\"reason\": \"Promoting religious conflict in diverse India\",\"severity\": \"High\"},{\"reason\": \"Inappropriate portrayal of a religious figure\",\"severity\": \"Medium\"},{\"reason\": \"Ignorance of Indian cultural and religious values\",\"severity\": \"Medium\"}]"
            },
            {
                "role":"user",
                "content":"a baby playing with toys"
            },
            {
                "role":"assistant",
                "content":"[]"
            },
            {
                "role":"user",
                "content":row[self.inputcolumn]
            }
        ]
        obj = {
            'messages': conversation,
            'max_tokens': 256,
            'temperature': 0.1,
            'top_p': 0.95,
            'frequency_penalty': 0,
            'presence_penalty': 0
        }
        return obj
    

    def gptScore(self, row):
        reqUrl = "https://gpt4-g11n.openai.azure.com/openai/deployments/gpt4/chat/completions?api-version=2023-07-01-preview"
        headers = {
            "api-key": secrets['gptkey'],
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        obj = self.message(row)
        try:
            start = time.time()
            x = requests.post(reqUrl, data=json.dumps(obj), headers=headers, timeout=30)
            end = time.time()
            x = json.loads(x.text)
            if 'error' in x:
                print("ERROR: " + row[self.inputcolumn] + " : " + x['error'])
                return row
            elif 'choices' in x:
                x = x['choices'][0]['message']['content']
                print("OUTPUT: " + row[self.inputcolumn] + " : " + x)
                row['reasons'] = x
                row['offensive'] = False
                reasons = json.loads(x)
                if len(reasons) > 0:
                    for item in reasons:
                        if item['severity'] == 'High':
                            row['offensive'] = True
                            break
                row['time'] = round(end - start, 2)
            return row
        except Exception as e:
            print(e)
            row['offensive'] = 'error'
            row['reasons'] = e
            return row


    def llamaScore(self, row):
        reqUrl = "http://0.0.0.0:6006/v1/chat/completions"
        headers = {
            "Authorization": "bearer " + secrets['imstoken'],
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": "contentauditor_web"
        }
        obj = self.message(row)
        try:
            start = time.time()
            x = requests.post(reqUrl, data=json.dumps(obj), headers=headers, timeout=30)
            end = time.time()
            x = json.loads(x.text)
            if 'error' in x:
                print("ERROR: " + row[self.inputcolumn] + " : " + x['error'])
                return row
            elif 'choices' in x:
                x = x['choices'][0]['message']['content']
                print("OUTPUT: " + row[self.inputcolumn] + " : " + x)
                row['offensive'] = x['offensive']
                row['reasons'] = x['reasons']
                row['time'] = end - start
            return row
        except Exception as e:
            print(e)
            row['offensive'] = 'error'
            row['reasons'] = e
            return row


_queryObj = _Query()
def Query(): return _queryObj