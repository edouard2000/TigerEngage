import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

class TextSummarizer:
    # Constructor
    def __init__(self):
        self.api_key = self.fetch_api_key()
        if not self.api_key:
            raise ValueError("OpenAI API key is not set.")
        self.openai_model = "gpt-3.5-turbo" 

    def fetch_api_key(self):
        return os.environ.get("OPENAI_API_KEY")

    def average_sentences(self, list_of_sentences):
        openai.api_key = self.api_key

        prompt = "These are answers provided by the students from the question they were asked, please provide a general summary of their answers. Do not give your own input, just summarize their answers:\n\n" + "\n".join(list_of_sentences)
        
        try:
            completion = openai.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a highly intelligent assistant capable of summarizing multiple sentences into a single coherent sentence."},
                    {"role": "user", "content": prompt}
                ]
            )

            summarized_sentence = completion.choices[0].message.content
            return summarized_sentence
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "An error occurred while generating the summary."

    def summarize_student_answers(self, question, student_answers, correct_answer):
        openai.api_key = self.api_key

        prompt = f"Question: {question}\n\nStudent answers:\n" + "\n".join([f"- {ans}" for ans in student_answers]) + \
                 f"\n\nCorrect answer: {correct_answer}\n\n" + \
                 "Summarize what students understand about the question, compare their understanding with the correct answer"

        try:
            completion = openai.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a highly intelligent assistant that can analyze student responses in the context of the given question and the correct answer."},
                    {"role": "user", "content": prompt}
                ]
            )
            summarized_response = completion.choices[0].message.content
            return summarized_response
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "An error occurred while generating the summary."

if __name__ == "__main__":
    summarizer = TextSummarizer()
    question = "Explain the difference between linear search and binary search."
    student_answers = [
        "Linear search goes one by one through the list, but binary search divides the list and eliminates half of it each time.",
        "Binary search is faster than linear search but requires the array to be sorted first.",
        "With linear search, you look at every element, which can be slow. Binary search is quicker but needs a sorted array.",
        "Linear search can be used on any list, sorted or not, but binary search cuts down the search area quickly in a sorted list."
    ]
    correct_answer = "Linear search sequentially checks each element of the list until a match is found or the whole list has been searched. Binary search, however, operates on a sorted array by repeatedly dividing the search interval in half."
    summary = summarizer.summarize_student_answers(question, student_answers, correct_answer)
    summary2 = summarizer.average_sentences(student_answers)
    print("Summary2 (Average Sentences):", summary2)
    print("Summary (Detailed Analysis):", summary)

