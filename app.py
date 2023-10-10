import streamlit as st
from wordcloud import WordCloud, STOPWORDS
from io import BytesIO
import base64
import os
from PyPDF2 import PdfReader


# Function to extract text from PDF file
def extract_text_from_pdf(file):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text() + "\n"
    return text

import zipfile
import xml.etree.ElementTree as ET

def extract_text_from_docx(file):
    with zipfile.ZipFile(file) as docx:
        content = docx.read('word/document.xml')
        root = ET.fromstring(content)
        paragraphs = root.findall('.//w:p')
        text = '\n'.join([''.join([node.text for node in p.findall('.//w:t')]) for p in paragraphs])
    return text


# Function to generate word cloud from text
def generate_word_cloud(text, stopwords):
    wc = WordCloud(width=800, height=400, background_color='white', stopwords=stopwords).generate(text)
    return wc

# Function to process uploaded files
def process_uploaded_files(uploaded_files):
    text = ""
    for file in uploaded_files:
        if file.name.endswith(".txt"):
            text += file.read().decode("utf-8")
        elif file.name.endswith(".pdf"):
            text += extract_text_from_pdf(file)
        elif file.name.endswith(".docx"):
            text += extract_text_from_docx(file)
    return text

# Streamlit app
def main():
    st.title("Word cloud app")
    
    st.sidebar.header("Options")
    remove_stopwords = st.sidebar.checkbox("Remove Stopwords")
    additional_stopwords = st.sidebar.text_area("Additional Stopwords (comma separated)")
    wordcloud_width = st.sidebar.number_input("Word Cloud Width", min_value=100, max_value=2000, value=800)
    wordcloud_height = st.sidebar.number_input("Word Cloud Height", min_value=100, max_value=2000, value=400)
    resolution = st.sidebar.number_input("Resolution (DPI)", min_value=10, max_value=300, value=100)
    save_as = st.sidebar.radio("Save Word Cloud As", ["PNG", "JPEG", "SVG"])


    uploaded_files = st.file_uploader("Upload document(s)", type=["txt", "pdf", "docx"], accept_multiple_files=True)

    if uploaded_files:
        text = process_uploaded_files(uploaded_files)

        if remove_stopwords:
            additional_stopwords_list = [word.strip() for word in additional_stopwords.split(",")]
            stopwords = set(additional_stopwords_list)
        else:
            stopwords = set(STOPWORDS)


        # Generate word cloud
        wc = generate_word_cloud(text, stopwords)
        
        # Display word cloud
        st.image(wc.to_image(), caption="Word Cloud", use_column_width=True)
        
        # Display top 50 words
        st.header("Top 50 Words")
        from collections import Counter

        # Tokenize the text into words
        words = text.split()

        # Remove stopwords
        filtered_words = [word for word in words if word.lower() not in stopwords]

        # Count word frequencies
        word_counts = Counter(filtered_words)

        # Get the top 50 words
        sorted_word_counts = word_counts.most_common(50)
        for word, count in sorted_word_counts:
            st.write(f"{word}: {count}")
    else:
        st.warning("Please upload a document.")

if __name__ == "__main__":
    main()
