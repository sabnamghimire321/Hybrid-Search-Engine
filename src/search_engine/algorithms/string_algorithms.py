def _build_lps(pattern: str) -> list[int]:
    lps = [0] * len(pattern)
    length = 0
    i = 1

    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1

    return lps

def kmp_search(text: str, pattern: str) -> list[int]:
    if not pattern or len(pattern) > len(text):
        return []

    lps = _build_lps(pattern)
    matches = []
    i = j = 0  
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == len(pattern):
                matches.append(i - j)
                j = lps[j - 1]  
        elif j != 0:
            j = lps[j - 1]
        else:
            i += 1

    return matches

def rabin_karp_search(text: str, pattern: str, base: int = 256, prime: int = 1_000_000_007) -> list[int]:
    n, m = len(text), len(pattern)
    if m == 0 or m > n:
        return []
    
    matches = []
    pattern_hash = 0
    window_hash = 0
    high_order = pow(base, m - 1, prime) 

    for i in range(m):
        pattern_hash = (pattern_hash * base + ord(pattern[i])) % prime
        window_hash = (window_hash * base + ord(text[i])) % prime

    for i in range(n - m + 1):
        if pattern_hash == window_hash:
            if text[i : i + m] == pattern:
                matches.append(i)

        if i < n - m:
            window_hash = (
                (window_hash - ord(text[i]) * high_order) * base + ord(text[i + m])
            ) % prime

    return matches