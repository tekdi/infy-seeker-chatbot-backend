from flask import Flask, request, jsonify
import re
import requests
from flask_cors import CORS
import pandas as pd
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from sklearn.feature_extraction.text import TfidfVectorizer
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
from googletrans import Translator
import gensim.downloader as api
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import time

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load dataset
dataset = pd.read_csv(r'NewData.csv')

# Initialize translator and seed for language detection
translator = Translator()
DetectorFactory.seed = 0

# Preprocess dataset
mapping = {
    "title": dataset.iloc[:, 1].tolist(),
    "description": dataset.iloc[:, 2].tolist()
}

def is_english(text):
    try:
        lang = detect(text)
        return lang == 'en'
    except LangDetectException:
        return False

def translate_text(text, src='hi', dest='en', retries=3):
    for attempt in range(retries):
        try:
            translation = translator.translate(text, src=src, dest=dest)
            return translation.text
        except Exception as e:
            print(f"Translation failed on attempt {attempt + 1}/{retries}: {e}")
            time.sleep(1)  # Wait a bit before retrying
    return text  # Return original text if all attempts fail

for i in range(len(mapping["title"])):
    if not isinstance(mapping["title"][i], str):
        mapping["title"][i] = str(mapping["title"][i])
    if not is_english(mapping["title"][i]):
        detector = detect(mapping["title"][i])
        translation = translator.translate(mapping["title"][i], src=detector, dest='en')
        mapping["title"][i] = translation.text

for j in range(len(mapping["description"])):
    if not isinstance(mapping["description"][j], str):
        mapping["description"][j] = str(mapping["description"][j])
    parts = re.split(r'\n\n\n|\n\n|\\n\\n', mapping["description"][j])
    mapping["description"][j] = parts[1] if len(parts) > 1 else mapping["description"][j]

df = pd.read_csv('NewData.csv')
df['translated_title'] = mapping["title"]
df.to_csv('NewData.csv', index=False)

# Function to get nouns and verbs from words
def get_nouns_and_verbs(words):
    tagged_words = pos_tag(words)
    return [word for word, pos in tagged_words]

# Function to extract relevant keyword
def extract_relevant_keyword(sentence):
    if isinstance(sentence, str):
        words = word_tokenize(sentence.lower())
    else:
        return None
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word.isalnum() and word not in stop_words]
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    filtered_words = get_nouns_and_verbs(lemmatized_words)
    if not filtered_words:
        return None
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([' '.join(filtered_words)])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[0]
    max_index = np.argmax(tfidf_scores)
    return feature_names[max_index]

# Extract most important words from each entry
most_important_titles = [extract_relevant_keyword(title) for title in mapping["title"]]
most_important_descriptions = [extract_relevant_keyword(desc) if desc != 'null' else "nothing" for desc in mapping["description"]]

# Load word embedding model
model = api.load("glove-wiki-gigaword-50")

def word_embedding_similarity(word1, word2):
    if word1 in model.key_to_index and word2 in model.key_to_index:
        return model.similarity(word1, word2)
    else:
        return 0

def remove_stopwords(sentence):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(sentence)
    return ' '.join([word for word in words if word.lower() not in stop_words and word.isalnum()])

def extract_keywords(text, num_keywords=3):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text])
    feature_names = vectorizer.get_feature_names_out()
    tfidf_scores = tfidf_matrix.toarray()[0]
    top_indices = tfidf_scores.argsort()[-num_keywords:][::-1]
    return [feature_names[index] for index in top_indices]

def parameter_runner(query):
    query = remove_stopwords(query.lower())
    keywords = extract_keywords(query)
    output_map = {"translated_title": None, "kahani_cache_dev__description": None}
    max_similarity = {"title": 0, "description": 0}
    for keyword in keywords:
        for title in most_important_titles:
            if title:
                sim = word_embedding_similarity(keyword, title)
                if sim > max_similarity["title"]:
                    max_similarity["title"] = sim
                    output_map["translated_title"] = title
        for description in most_important_descriptions:
            if description:
                sim = word_embedding_similarity(keyword, description)
                if sim > max_similarity["description"]:
                    max_similarity["description"] = sim
                    output_map["kahani_cache_dev__description"] = description
    return output_map

@app.route('/process', methods=['POST'])
def process_query():
    data = request.json
    query = data.get('query', '')
    if not is_english(query):
        detected_lang = detect(query)
        query = translator.translate(query, src = detected_lang, dest = 'en').text
    answer = parameter_runner(query)
    search_key1 = 'translated_title'
    search_value1 = answer[search_key1]
    search_key2 = 'kahani_cache_dev__description'
    search_value2 = answer[search_key2]
    matching_entries = df[df[search_key1].str.contains(search_value1, case=False) | df[search_key2].str.contains(search_value2, case=False)]
    selected_columns = matching_entries.iloc[:, 1:3]
    matching_entries_dict = selected_columns.to_dict(orient='records')
    node_server_url = "http://127.0.0.1:3000/search"
    try:
        response = requests.post(node_server_url, json={"results": matching_entries_dict})
        response.raise_for_status()
        node_response = response.json()
    except requests.exceptions.RequestException as e:
        node_response = {"error": str(e)}
    return jsonify({
        "status": "success" if "error" not in node_response else "error",
        "data": matching_entries_dict,
        "node_response": node_response
    })

if __name__ == '__main__':
    app.run(debug=True)
