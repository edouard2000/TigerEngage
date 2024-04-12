import pyaudio
import wave
import whisper

# Initialize the Whisper model
model = whisper.load_model("base")

# Setup audio stream parameters
CHUNK = 4096  # Number of audio frames per buffer
FORMAT = pyaudio.paInt16  # Audio format (16-bit PCM)
CHANNELS = 1  # Single channel for microphone
RATE = 16000  # Sample rate

audio_interface = pyaudio.PyAudio()

stream = audio_interface.open(format=FORMAT,
                              channels=CHANNELS,
                              rate=RATE,
                              input=True,
                              frames_per_buffer=CHUNK)

print("Recording...")

frames = []

# Capture audio data for a specified duration
for _ in range(0, int(RATE / CHUNK * 5)):  # Adjust the range for duration needed
    data = stream.read(CHUNK)
    frames.append(data)

print("Finished recording.")

# Stop and close the stream 
stream.stop_stream()
stream.close()
audio_interface.terminate()

# Save the captured audio to a WAV file
with wave.open("output.wav", "wb") as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio_interface.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b"".join(frames))

# Transcribe the recorded audio
transcription = model.transcribe("output.wav")
print("Transcription: ", transcription['text'])
