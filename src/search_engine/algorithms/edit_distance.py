def levenshtein_distance(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a  

    if len(b) == 0:
        return len(a)

    previous_row = list(range(len(b) + 1))

    for i, char_a in enumerate(a, start=1):
        current_row = [i] + [0] * len(b)

        for j, char_b in enumerate(b, start=1):
            if char_a == char_b:
                current_row[j] = previous_row[j - 1]
            else:
                current_row[j] = 1 + min(
                    previous_row[j - 1],  
                    previous_row[j],     
                    current_row[j - 1],  
                )

        previous_row = current_row

    return previous_row[-1]