import PyPDF2
from nltk.tokenize import sent_tokenize
from Audio_processing import get_embeddings

# Constants
SENTENCES_PER_SEGMENT = 4

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    :param pdf_path: Path to the PDF file.
    :return: Extracted text as a string.
    """
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfFileReader(file)
            full_text = ''.join([reader.getPage(page).extractText() for page in range(reader.numPages)])
        return full_text
    except Exception as e:
        print(f"Error reading PDF file: {e}")
        return None

def generate_embeddings_from_text(text, sentences_per_segment=SENTENCES_PER_SEGMENT):
    """
    Generates embeddings for segments of the given text.
    :param text: Text to process.
    :param sentences_per_segment: Number of sentences per text segment for embedding.
    :return: Dictionary of embeddings for each text segment.
    """
    embeddings = {}
    sentences = sent_tokenize(text)
    for i in range(0, len(sentences), sentences_per_segment):
        segment = ' '.join(sentences[i:i + sentences_per_segment])
        embedding = get_embeddings(segment)
        embeddings[i // sentences_per_segment + 1] = [embedding, segment]
    return embeddings

def extract_text_and_process(pdf_path):
    """
    Extracts text from a PDF and generates embeddings for each segment.
    :param pdf_path: Path to the PDF file.
    :return: Dictionary of embeddings for each text segment.
    """
    full_text = extract_text_from_pdf(pdf_path)
    if full_text is not None:
        return generate_embeddings_from_text(full_text)
    else:
        return {}
