import whisper

def transcribe_audio(audio_path):
    # Load the Whisper model
    model = whisper.load_model("tiny")  # You can choose other models like 'tiny', 'small', 'medium', or 'large' based on your needs and resources.

    # Load and transcribe the audio
    result = model.transcribe(audio_path, fp16=False)

    # Print the transcription
    print("Transcription: ", result['text'])

# Replace 'path_to_your_audio_file.wav' with the path to your actual audio file
print(transcribe_audio("count.mp3"))
