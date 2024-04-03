#!/usr/bin/env python

# --------------------------------------------------------------------------
# summarizer.py
# Authors: Wangari Karani, Roshaan Khalid, Jourdain Babisa, Edouard Kwizera
# --------------------------------------------------------------------------

import os
from openai import OpenAI

# --------------------------------------------------------------------------

# Instantiate a client to ChatGPT and grab the API key from the .env file
client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY")
)

completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
  ]
)

print(completion.choices[0].message)

# print(completion.choices[0].message.content)

# client.close()

# --------------------------------------------------------------------------

# Write the text summarizer class
class GenerateFeedback:

    # ChatGPT Model that we're using
    openai_model = "gpt-3.5-turbo"

    # constructor
    def __init__(self) -> None:
        self.apikey = os.environ.get("OPENAI_API_KEY")

    # Method to get API Key
    def fetch_api_key(self):
        return os.environ.get("OPENAI_API_KEY")
    
    # Take list of student responses and generate a summary/average sentence
    def answers_summary(self, list_of_student_answers):
        # Instantiate the client
        client = OpenAI(api_key=self.apikey)

        # Write chatGPT prompt to execute the task
        prompt = "Here is a list of multiple student answers that I want you to summarize and rewrite as a single sentence that is roughly the same length as the input sentences. The sentences are separated by newline characters \n as follows: {answers}"
        prompt = prompt.format(answers = "\n".join(list_of_student_answers))

        # Make chatGPT request
        completion = client.chat.completions.create(
        model=self.openai_model,
        messages=[
            {"role": "system", "content": " Insert what we want chatGPT to do"},
            {"role": "user", "content": prompt}
        ]
        )

        # Get the summary of the answers
        summarized_answer = completion.choices[0].message

        # Close the client
        client.close()

        return summarized_answer
    
# --------------------------------------------------------------------------

gpt_summarizer = GenerateFeedback()

gpt_summarizer.answers_summary([' pass in student answers '])
        