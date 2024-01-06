import requests, json, time
from utils import Prefs
from dotenv import load_dotenv, dotenv_values

load_dotenv()
secrets = dotenv_values(".env")

class _Query:
    inputcolumn = None
    region = 'worldwide'
    llm = None
    endpoint = None
    header = {}

    def __init__(self):
        self.inputcolumn = Prefs().getPref('inputcolumn', 'csv')
        self.region = Prefs().getPref('region')
        self.llm = Prefs().getPref('llm')
        self.endpoint = Prefs().getPref('url', self.llm)
        self.header = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }


    def getMessage(self, row):
        context = "Provide a list of reasons with each reason described in around 10 words in JSON format along with their severity (categorized as High, Medium, and Low) for the last user-provided text input to be culturally offensive to the majority of people in " + self.region + ". Don't make any presumptions and only consider the user-provided text input for evaluation. Merge similar reasons together and provide the response within 150 words. Only provide a valid JSON in the response. Do not provide any explanations, examples or notes."
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
            'presence_penalty': 0,
            'model': './model/mixtral_8x7b'
        }
        return obj


    def ask(self, row):
        reqUrl = self.endpoint
        obj = self.getMessage(row)

        try:
            start = time.time()
            x = requests.post(reqUrl, data=json.dumps(obj), headers=self.header, timeout=30)
            end = time.time()
            x = json.loads(x.text)
            if 'choices' in x:
                if x['choices'][0]['message']['content'] != None:
                    x = x['choices'][0]['message']['content']
                    major = []
                    minor = []
                    row[self.llm + ' offensive'] = False
                    reasons = json.loads(x)
                    if len(reasons) > 0:
                        for item in reasons:
                            if item['severity'] == 'High':
                                row[self.llm + ' offensive'] = True
                                major.append(item['reason'])
                            elif item['severity'] == 'Medium':
                                minor.append(item['reason'])
                    row[self.llm + ' major reasons'] = ' | '.join(major)
                    row[self.llm + ' minor reasons'] = ' | '.join(minor)
                    row[self.llm + ' time'] = round(end - start, 2)
                    print("OUTPUT: " + row[self.inputcolumn] + " : " + str(row[self.llm + ' offensive']))
                else:
                    print("ERROR: " + row[self.inputcolumn] + " : " + 'content filtered')
                    return row
            elif 'message' in x:
                print("ERROR: " + row[self.inputcolumn] + " : " + x['message'])
                return row
            return row
        except Exception as e:
            print(e)
            row[self.llm + ' offensive'] = 'error'
            row[self.llm + ' major reasons'] = e
            return row


_queryObj = _Query()
def Query(): return _queryObj.ask