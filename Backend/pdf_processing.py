import PyPDF2
from nltk.tokenize import sent_tokenize
from Audio_processing import get_embeddings

def extract_text_and_process(pdf_path):
    # Function to generate embeddings for a text segment
    # Reading the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        num_pages = reader.numPages

        # Extracting text from each page
        full_text = ''
        for page in range(num_pages):
            full_text += reader.getPage(page).extractText()

    # Tokenize the text into sentences
    sentences = sent_tokenize(full_text)

    # Breaking the text into segments of four sentences each
    embeddings = {}
    index = 1  # Start index for dictionary keys
    for i in range(0, len(sentences), 4):
        segment = ' '.join(sentences[i:i + 4])
        embedding = get_embeddings(segment)
        embeddings[index] = [embedding, segment]
        index += 1

    return embeddings