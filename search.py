import re
from sklearn.feature_extraction.text import TfidfVectorizer

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z ]', '', text)
    return text.split()

def boolean_search(query, docs):
    query = query.lower()

    if " and " in query:
        terms = [t.strip() for t in query.split(" and ")]
        operator = "and"
    elif " or " in query:
        terms = [t.strip() for t in query.split(" or ")]
        operator = "or"
    elif " not " in query:
        terms = [t.strip() for t in query.split(" not ")]
        operator = "not"
    else:
        terms = preprocess(query)   
        operator = "single"

    results = []

    for doc in docs:
        processed_doc = preprocess(doc)
        words = set(processed_doc)

        # Exact match boost
        if preprocess(query) == processed_doc:
            results.insert(0, doc)
            continue

        if operator == "and":
            if all(term in words for term in terms):
                results.append(doc)

        elif operator == "or":
            if any(term in words for term in terms):
                results.append(doc)

        elif operator == "not":
            if not any(term in words for term in terms):
                results.append(doc)

        else:
            if any(term in words for term in terms):
                results.append(doc)

    return results


def rank_documents(query, docs):
    if not docs:
        return []

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(docs)
    query_vec = vectorizer.transform([query])

    scores = (tfidf_matrix @ query_vec.T).toarray()

    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)

    return ranked