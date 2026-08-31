import math

def dot_product(vector_a: dict[str, float], vector_b: dict[str, float]) -> float:
    smaller, larger = (vector_a, vector_b) if len(vector_a) <= len(vector_b) else (vector_b, vector_a)
    return sum(weight * larger.get(term, 0.0) for term, weight in smaller.items())

def magnitude(vector: dict[str, float]) -> float:
    return math.sqrt(sum(weight * weight for weight in vector.values()))

def cosine_similarity(vector_a: dict[str, float], vector_b: dict[str, float]) -> float:
    mag_a = magnitude(vector_a)
    mag_b = magnitude(vector_b)

    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0

    return dot_product(vector_a, vector_b) / (mag_a * mag_b)