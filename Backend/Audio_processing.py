from pydub import AudioSegment
import whisper
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize
from openai import OpenAI

# Function to get embeddings from OpenAI
def get_embeddings(text):
   client = OpenAI()
   response = client.embeddings.create(
	input=text,
	model="text-embedding-ada-002"
	)
   if response.status_code == 200:
        return response.data[0].embedding
   else:
        raise Exception(f"Error in OpenAI API call: {response.text}")

def split_audio(filepath, one_hour=60 * 60 * 1000):  # One hour in milliseconds
    # Load the MP3 file
    audio = AudioSegment.from_mp3(filepath)
    duration = len(audio)
    full_transcript = ""  # Initialize an empty string for the full transcript
    model = whisper.load_model("base")  # Load the Whisper model

    for start in range(0, duration, one_hour):
        end = min(start + one_hour, duration)
        segment = audio[start:end]
        segment_file = f"{filepath}_part{start // one_hour}.wav"
        segment.export(segment_file, format="wav")  # Export as WAV

        # Transcribe the segment and append to the full transcript
        result = model.transcribe(segment_file)
        full_transcript += result['text'] + " "

    return full_transcript.strip()  # Return the combined transcript


def transcribe_audio(full_transcript):
    embeddings = {}
    index = 1  # Start index for dictionary keys
    sentences = sent_tokenize(full_transcript)

    # Breaking the full transcript into segments of four sentences each
    for i in range(0, len(sentences), 4):
        segment = ' '.join(sentences[i:i + 4])
        embedding = get_embeddings(segment)
        embeddings[index] = [embedding, segment]
        index += 1

    return embeddings

