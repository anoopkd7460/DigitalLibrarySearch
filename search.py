import string
from sklearn.feature_extraction.text import TfidfVectorizer

# NLP
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
# Initialize
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

# -------------------------------
# POS Mapping
# -------------------------------
def get_wordnet_pos(tag):    #NNP,VBZ,DT,RB,JJ,NN
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    return wordnet.NOUN


# -------------------------------
# Preprocessing (Lemmatization)
# -------------------------------
def preprocess(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))

    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)  #List of tuples

    tokens = [
        lemmatizer.lemmatize(word, get_wordnet_pos(tag))
        for word, tag in tagged
        if word not in stop_words
    ]

    return tokens


# -------------------------------
# Boolean Search
# -------------------------------
def boolean_search(query, docs):
    query = query.lower()

    include_terms = []
    exclude_terms = []
    operator = "single"

    if " and " in query:
        include_terms = [t.strip() for t in query.split(" and ")]
        operator = "and"

    elif " or " in query:
        include_terms = [t.strip() for t in query.split(" or ")]
        operator = "or"

    elif " not " in query:
        parts = query.split(" not ")
        include_terms = [parts[0].strip()]
        exclude_terms = [parts[1].strip()]
        operator = "not"

    else:
        include_terms = preprocess(query)

    results = []

    for doc in docs:
        processed_doc = preprocess(doc)
        words = set(processed_doc)

        include_terms_processed = [
            w for term in include_terms for w in preprocess(term)
        ]
        exclude_terms_processed = [
            w for term in exclude_terms for w in preprocess(term)
        ]

        if operator == "and":
            if all(term in words for term in include_terms_processed):
                results.append(doc)

        elif operator == "or":
            if any(term in words for term in include_terms_processed):
                results.append(doc)

        elif operator == "not":
            if (
                any(term in words for term in include_terms_processed)
                and not any(term in words for term in exclude_terms_processed)
            ):
                results.append(doc)

        else:
            if any(term in words for term in include_terms_processed):
                results.append(doc)

    return results


# -------------------------------
# Ranking (TF-IDF + Boost)
# -------------------------------
def rank_documents(query, docs):
    if not docs:
        return []

    processed_docs = [" ".join(preprocess(doc)) for doc in docs]
    processed_query = " ".join(preprocess(query))

    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2)
    )

    tfidf_matrix = vectorizer.fit_transform(processed_docs)
    query_vec = vectorizer.transform([processed_query])

    scores = (tfidf_matrix @ query_vec.T).toarray().flatten()

    ranked = []
    for doc, score in zip(docs, scores):

        # Boost if exact phrase match
        if query.lower() in doc.lower():
            score += 0.2

        ranked.append((doc, score))

    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked
