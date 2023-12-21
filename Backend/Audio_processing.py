import os
from pydub import AudioSegment
import whisper
import nltk
from Open_AI_functions import OpenAIClient
from nltk.tokenize import sent_tokenize

# Constants
ONE_HOUR_MS = 60 * 60 * 1000  # One hour in milliseconds
SENTENCES_PER_SEGMENT = 4  # Number of sentences per text segment for embedding

# Ensure necessary NLTK data is downloaded
nltk.download('punkt')

def split_audio(filepath):
    """
    Splits an audio file into one-hour segments and transcribes them.
    :param filepath: Path to the audio file.
    :return: Full transcribed text of the audio.
    """
    try:
        audio = AudioSegment.from_mp3(filepath)
        duration = len(audio)
        full_transcript = ""
        model = whisper.load_model("base")

        for start in range(0, duration, ONE_HOUR_MS):
            end = min(start + ONE_HOUR_MS, duration)
            segment = audio[start:end]
            segment_file = f"{os.path.splitext(filepath)[0]}_part{start // ONE_HOUR_MS}.wav"
            segment.export(segment_file, format="wav")

            result = model.transcribe(segment_file)
            full_transcript += result['text'] + " "

        return full_transcript.strip()
    except Exception as e:
        print(f"Error processing audio file: {e}")
        return None

def transcribe_audio(full_transcript):
    """
    Generates embeddings for segments of the transcript.
    :param full_transcript: The full text transcript of an audio file.
    :return: Dictionary of embeddings for each text segment.
    """
    embeddings = {}
    index = 1
    sentences = sent_tokenize(full_transcript)

    openai_client = OpenAIClient()

    for i in range(0, len(sentences), SENTENCES_PER_SEGMENT):
        segment = ' '.join(sentences[i:i + SENTENCES_PER_SEGMENT])
        embedding = openai_client.get_embeddings(segment)
        embeddings[index] = [embedding, segment]
        index += 1

    return embeddings
