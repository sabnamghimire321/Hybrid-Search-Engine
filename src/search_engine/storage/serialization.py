import struct

from search_engine.core.index.inverted_index import InvertedIndex

MAGIC = b"SEIX"  
VERSION = 1

def serialize_index(index: InvertedIndex) -> bytes:
    buffer = bytearray()
    buffer += MAGIC
    buffer += struct.pack("<I", VERSION)

    doc_ids = sorted(index.all_document_ids())
    buffer += struct.pack("<I", len(doc_ids))
    for doc_id in doc_ids:
        buffer += struct.pack("<II", doc_id, index.document_length(doc_id))

    terms = index.all_terms()
    buffer += struct.pack("<I", len(terms))
    for term in terms:
        term_bytes = term.encode("utf-8")
        buffer += struct.pack("<H", len(term_bytes))
        buffer += term_bytes

        postings = index.get_postings(term)
        buffer += struct.pack("<I", len(postings))
        for doc_id, positions in postings.items():
            buffer += struct.pack("<I", doc_id)
            buffer += struct.pack("<I", len(positions))
            for pos in positions:
                buffer += struct.pack("<I", pos)

    return bytes(buffer)

def deserialize_index(data: bytes) -> InvertedIndex:
    offset = 0

    magic = data[offset : offset + 4]
    offset += 4
    if magic != MAGIC:
        raise ValueError("Not a valid search engine index file (bad magic bytes)")

    (version,) = struct.unpack_from("<I", data, offset)
    offset += 4
    if version != VERSION:
        raise ValueError(f"Unsupported index format version: {version}")

    (num_docs,) = struct.unpack_from("<I", data, offset)
    offset += 4
    doc_lengths: dict[int, int] = {}
    for _ in range(num_docs):
        doc_id, length = struct.unpack_from("<II", data, offset)
        offset += 8
        doc_lengths[doc_id] = length

    (num_terms,) = struct.unpack_from("<I", data, offset)
    offset += 4
    term_postings: dict[str, dict[int, list[int]]] = {}

    for _ in range(num_terms):
        (term_len,) = struct.unpack_from("<H", data, offset)
        offset += 2
        term = data[offset : offset + term_len].decode("utf-8")
        offset += term_len

        (num_postings,) = struct.unpack_from("<I", data, offset)
        offset += 4
        postings: dict[int, list[int]] = {}

        for _ in range(num_postings):
            (doc_id,) = struct.unpack_from("<I", data, offset)
            offset += 4
            (num_positions,) = struct.unpack_from("<I", data, offset)
            offset += 4
            positions = list(struct.unpack_from(f"<{num_positions}I", data, offset))
            offset += 4 * num_positions
            postings[doc_id] = positions

        term_postings[term] = postings

    index = InvertedIndex()
    index.bulk_load(term_postings, doc_lengths)
    return index