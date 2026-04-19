import re
from sklearn.feature_extraction.text import TfidfVectorizer

def preprocess(text):
    text = text.lower()
    text = re.sub(r'[^a-z ]', '', text)
    return text.split()

def boolean_search(query, docs):
    query = query.lower()

    # ---- Detect query type ----
    if query.startswith("not "):
        # Case: NOT banana
        exclude_terms = preprocess(query[4:])
        operator = "not_only"

    elif " and " in query:
        terms = [t.strip() for t in query.split(" and ")]
        operator = "and"
    elif " or " in query:
        terms = [t.strip() for t in query.split(" or ")]
        operator = "or"
    elif " not " in query:
        # Case: apple NOT banana
        include_part, exclude_part = query.split(" not ", 1)
        include_terms = preprocess(include_part)
        exclude_terms = preprocess(exclude_part)
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
            # A NOT B  → include A, exclude B
            if (all(term in words for term in include_terms) 
            and not any(term in words for term in exclude_terms)):
                results.append(doc)

        elif operator == "not_only":
            # NOT B → exclude B
            if not any(term in words for term in exclude_terms):
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
