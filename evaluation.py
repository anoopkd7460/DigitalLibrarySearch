def evaluate(retrieved, relevant):
    retrieved = set(retrieved)
    relevant = set(relevant)

    tp = len(retrieved & relevant)

    precision = tp / len(retrieved) if retrieved else 0
    recall = tp / len(relevant) if relevant else 0

    if precision + recall == 0:
        f1 = 0
    else:
        f1 = 2*(precision * recall) / (precision + recall)

    return precision,recall, f1