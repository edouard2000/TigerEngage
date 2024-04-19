import os
from dotenv import load_dotenv
import openai
load_dotenv()

class LectureNoteSummarizer:
    # Constructor
    def __init__(self):
        self.api_key = self.fetch_api_key()
        if not self.api_key:
            raise ValueError("OpenAI API key is not set.")
        self.openai_model = "gpt-3.5-turbo"  

    def fetch_api_key(self):
        return os.environ.get("OPENAI_API_KEY")

    def create_concise_notes(self, transcript):
        openai.api_key = self.api_key

        prompt = "Convert the following lecture transcript into concise, bullet-point notes that capture the key points and concepts:\n\n" + transcript
        
        try:
            completion = openai.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "Generate concise, bullet-point notes from the transcript."},
                    {"role": "user", "content": prompt}
                ]
            )

            notes = completion.choices[0].message.content
            return notes
        except Exception as e:
            print(f"Error generating notes: {e}")
            return "An error occurred while generating the notes."

if __name__ == "__main__":
    summarizer = LectureNoteSummarizer()
    transcript = """
    Today we discussed the principles of neural networks and deep learning. We started with the basics of neural network architecture, including neurons, weights, biases, and activation functions. We then explored how networks are trained using a backpropagation algorithm to adjust weights based on errors. Lastly, we looked at applications of deep learning in image recognition, natural language processing, and more.
    """
    notes = summarizer.create_concise_notes(transcript)
    print("Generated Notes:")
    print(notes)
