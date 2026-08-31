DOCUMENTS: dict[int, str] = {
    1: "Python is a high-level programming language known for its clean, "
       "readable syntax. It supports object-oriented, functional, and "
       "procedural programming paradigms.",
    2: "Python is widely used in data science and machine learning due to "
       "libraries like NumPy, pandas, and scikit-learn.",
    3: "JavaScript is the primary language for web browser scripting. "
       "Modern JavaScript frameworks include React, Vue, and Angular.",
    4: "Web development involves building websites and web applications "
       "using HTML, CSS, and JavaScript for the frontend.",
    5: "Machine learning is a subset of artificial intelligence that "
       "enables systems to learn patterns from data without explicit "
       "programming.",
    6: "Deep learning uses neural networks with many layers to model "
       "complex patterns, and has driven major advances in computer "
       "vision and natural language processing.",
    7: "Natural language processing combines linguistics and machine "
       "learning to help computers understand and generate human "
       "language.",
    8: "REST APIs allow web applications to communicate over HTTP using "
       "standard methods like GET, POST, PUT, and DELETE.",
    9: "Database indexing improves query performance by allowing the "
       "database engine to find rows without scanning an entire table.",
    10: "An inverted index maps each word to the list of documents "
        "containing it, forming the core data structure behind most "
        "search engines.",
    11: "Italian cuisine is known for its regional diversity, emphasizing "
        "fresh ingredients like tomatoes, olive oil, and fresh pasta.",
    12: "Baking bread requires understanding yeast fermentation, gluten "
        "development, and precise temperature control.",
    13: "Software engineering best practices include writing tests, "
        "code review, version control with git, and continuous "
        "integration pipelines.",
    14: "Python's popularity in software engineering comes partly from "
        "its extensive standard library and the readability of its "
        "syntax, which reduces long-term maintenance costs.",
    15: "Search engines rank documents using signals like term "
        "frequency, document frequency, and increasingly, semantic "
        "similarity from neural embeddings.",
}

RELEVANCE_JUDGMENTS: dict[str, dict[int, int]] = {
    "python programming language": {
        1: 3,  
        14: 2,  
        2: 1,   
    },
    "machine learning and neural networks": {
        6: 3,   
        5: 3,   
        7: 2,  
        2: 1,  
    },
    "web development frameworks": {
        4: 3,  
        3: 2,   
        8: 1,   
    },
    "search engine indexing": {
        10: 3,  
        15: 3,  
        9: 2,   
    },
}

def relevant_doc_ids(query: str) -> set[int]:
    """Binary relevant/not-relevant set (relevance >= 1), for
    precision/recall which don't use graded relevance."""
    return {doc_id for doc_id, grade in RELEVANCE_JUDGMENTS[query].items() if grade >= 1}