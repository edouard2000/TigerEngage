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

    def learn_more(self, question, correct_answer):
        openai.api_key = self.api_key

        prompt = (f"Question: {question}\n"
                f"Correct answer: {correct_answer}\n"
                f"Explain why this is the correct answer by relating key elements of the question to the answer. "
                f"Provide a clear and concise explanation, keeping it under 500 characters.")

        try:
            completion = openai.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a highly intelligent assistant tasked with explaining why specific answers are correct in relation to the question's key elements. Provide a clear and concise explanation, ideally under 100 characters."},
                    {"role": "user", "content": prompt}
                ]
            )

            enhanced_explanation = completion.choices[0].message.content
            # Automatically truncate to ensure it does not exceed 100 characters
            return enhanced_explanation[:500]
        except Exception as e:
            print(f"Error generating enhanced explanation: {e}")
            return "An error occurred while generating the enhanced explanation."




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
    question = "How binary search work"
    student_answers = [
        "Linear search goes one by one through the list, but binary search divides the list and eliminates half of it each time.",
        "Binary search is faster than linear search but requires the array to be sorted first.",
        "With linear search, you look at every element, which can be slow. Binary search is quicker but needs a sorted array.",
        "Linear search can be used on any list, sorted or not, but binary search cuts down the search area quickly in a sorted list."
    ]
    correct_answer = "Repeatedly dividing in half the portion of the list that could contain the item, until you've narrowed down the possible locations to just one"
    summary = summarizer.summarize_student_answers(question, student_answers, correct_answer)
    summary2 = summarizer.learn_more(question, correct_answer)
    print("Summary (Detailed Analysis):", summary2)