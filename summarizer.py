import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

class GenerateFeedback:
    def __init__(self):
        self.openai_model = "text-davinci-003"  # Adjust as needed
        self.api_key = os.environ.get("OPENAI_API_KEY")

    def answers_summary(self, correct_answer, list_of_student_answers):
        if not self.api_key:
            raise ValueError("OpenAI API key is not set.")
            
        openai.api_key = self.api_key

        prompt = f"Here is the correct answer to a question: '{correct_answer}'. Below are multiple student answers:\n\n" + \
                 "\n\n".join(f"- {answer}" for answer in list_of_student_answers) + \
                 "\n\nSummarize the key points made by the students, comparing them to the correct answer."

        try:
            completion = openai.Completion.create(
              engine=self.openai_model,
              prompt=prompt,
              max_tokens=150,
              temperature=0.7,
              n=1,
              stop=None
            )

            summary = completion.choices[0].text.strip()
            return summary
        except Exception as e:
            print(f"Error generating summary: {e}")
            return None

# Example usage
if __name__ == "__main__":
    gf = GenerateFeedback()
    summary = gf.answers_summary("The capital of France is Paris.", ["Paris is the capital", "I think it's Paris", "Isn't it Paris?"])
    print(summary)
