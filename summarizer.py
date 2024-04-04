#!/usr/bin/env python

# --------------------------------------------------------------------------
# summarizer.py
# Authors: Wangari Karani, Roshaan Khalid
# --------------------------------------------------------------------------

import os
from openai import OpenAI

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
    def answers_summary(self, correct_answer, list_of_student_answers):
        # Instantiate the client
        client = OpenAI(api_key=self.apikey)

        # Write chatGPT prompt to execute the task
        prompt = "Here is the correct answer to a question: {correct_answer}, and here is a list of multiple student answers separated by newline characters \n that I want you to compare against the correct answer provided and generate a summary of the students' overall performance: {answers}"
        prompt = prompt.format(correct_answer = correct_answer, answers = "\n".join(list_of_student_answers))

        # Make chatGPT request
        completion = client.chat.completions.create(
        model=self.openai_model,
        messages=[
            {"role": "system", "content": "You are an assistant that can read a list of student answers which may be written slightly differently with different variations and possibly with typos, and compare these answers against the correct answer provided. You are an expert at reading the list of answers (with all their variations) and returning a summary of the students' overall performance on whatever the question was."},
            {"role": "user", "content": prompt}
        ]
        )

        # Get the summary of the answers
        summary = completion.choices[0].message

        # Close the client
        client.close()

        return summary