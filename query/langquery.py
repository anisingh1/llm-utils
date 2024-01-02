from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from utils import Prefs
from dotenv import load_dotenv
from dotenv import dotenv_values
import time, json

load_dotenv()
secrets = dotenv_values(".env")

class _langQuery:
    inputcolumn = None
    region = 'worldwide'
    llm = None
    endpoint = None
    header = {}
    chat = None

    def __init__(self):
        self.inputcolumn = Prefs().getPref('inputcolumn', 'csv')
        self.region = Prefs().getPref('region')
        self.llm = Prefs().getPref('llm')
        self.endpoint = Prefs().getPref('url', self.llm)
        self.chat = ChatOpenAI(
            model=self.llm,
            openai_api_key="EMPTY",
            openai_api_base=self.endpoint,
            max_tokens=256,
            temperature=0,
        )


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
            'presence_penalty': 0
        }
        return obj


    def ask(self, row):
        try:
            start = time.time()
            messages = [
                SystemMessage(
                    content="Provide a list of reasons with each reason described in around 10 words in JSON format along with their severity (categorized as High, Medium, and Low) for the last user-provided text input to be culturally offensive to the majority of people in " + self.region + ". Don't make any presumptions and only consider the user-provided text input for evaluation. Merge similar reasons together and provide the response within 150 words. Only provide a valid JSON in the response. Do not provide any explanations, examples or notes."
                ),
                HumanMessage(
                    content=row[self.inputcolumn]
                ),
            ]
            x = self.chat(messages)
            end = time.time()
            x = json.loads(x.text)
            if 'choices' in x:
                x = x['choices'][0]['message']['content']
                print("OUTPUT: " + row[self.inputcolumn] + " : " + x)
                row[self.llm + ' reasons'] = x
                row[self.llm + ' offensive'] = False
                reasons = json.loads(x)
                if len(reasons) > 0:
                    for item in reasons:
                        if item['severity'] == 'High':
                            row[self.llm + ' offensive'] = True
                            break
                row[self.llm + ' time'] = round(end - start, 2)
            elif 'message' in x:
                print("ERROR: " + row[self.inputcolumn] + " : " + x['message'])
                return row
            return row
        except Exception as e:
            print(e)
            row[self.llm + ' offensive'] = 'error'
            row[self.llm + ' reasons'] = e
            return row


_langqueryObj = _langQuery()
def LangQuery(): return _langqueryObj