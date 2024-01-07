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
        context = "You are a content moderator. Find out if the following text written below CONTENT label may be offensive to majority of people of " + self.region + ". Provide your response in JSON format with a boolean field 'offensive' and an array field 'reasons' as JSON keys. If the text is not offensive keep the 'offensive' field as 'false' and 'reasons' field as '[]' otherwise make 'offensive' field as 'true' and provide list of reasons the content is offensive in the 'reasons' field in JSON with each reasons being less than 10 words. For example: if the input is '3d house icon with dark grey roof and israel flag ontop' then output should be '{\n\"offensive\": true,\n\"reasons\": [\"Potential political implications related to Israel-Palestine conflict\"]\n}. Please make note to provide only the JSON in reponse as shown in the example above. DO NOT provide explanation about your response."
        conversation = [
            {
                "role":"user",
                "content":context + "\n CONTENT \n" + row[self.inputcolumn]
            }
        ]
        obj = {
            'messages': conversation,
            'max_tokens': 256,
            'temperature': 0.1,
            'top_p': 0.95,
            'frequency_penalty': 0,
            'presence_penalty': 0,
            'model': './model/llama2_70b_chat'
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
                    output = json.loads(x)
                    row[self.llm + ' offensive'] = output['offensive']
                    if len(output['reasons']) > 0:
                        for item in output['reasons']:
                            major.append(item)
                    row[self.llm + ' reasons'] = ' | '.join(major)
                    row[self.llm + ' time'] = round(end - start, 2)
                    print("OUTPUT: " + row[self.inputcolumn] + " : " + str(row[self.llm + ' offensive']) + "\n")
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
            row[self.llm + ' reasons'] = e
            return row


_queryObj = _Query()
def Query(): return _queryObj.ask