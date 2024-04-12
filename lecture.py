from openai import OpenAI
import os
import speech_mic
import speech2text

# Initialize the OpenAI client with the API key from the environment
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)


class TextSummarizer:
    openai_model = "gpt-3.5-turbo"

   
    def __init__(self):
        self.apikey = self.fetch_api_key()

   
    def fetch_api_key(self):
        return os.environ.get("OPENAI_API_KEY")


    def convert_lecture_to_notes(self, lecture_text):
       
        client = OpenAI(api_key=self.apikey)
        completion = client.chat.completions.create(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": "You are an assistant that converts detailed lecture content into concise notes."},
                {"role": "user", "content": lecture_text}
            ]
        )
        notes = completion.choices[0].message.content
        client.close() 
        return notes

   
gpt_summarizer = TextSummarizer()

lecture_text = "So, when you have different arrays in java, make sure to assign them properly"
notes = gpt_summarizer.convert_lecture_to_notes(lecture_text)
print("Generated Notes:\n", notes)

