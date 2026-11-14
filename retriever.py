
import re


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def retrieve(
    query: str,
    documents: list[str],
    k: int = 3
) -> list[str]:
    if k <= 0:
        return []

    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    scored = []
    for document in documents:
        document_tokens = tokenize(document)
        score = len(query_tokens & document_tokens)

        if score > 0:
            scored.append((score, document))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [document for _, document in scored[:k]]
