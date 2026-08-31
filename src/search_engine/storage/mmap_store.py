import mmap
import struct

MAGIC = b"SEIM"  
VERSION = 1

def write_mmap_index(
    doc_lengths: dict[int, int],
    term_postings: dict[str, dict[int, list[int]]],
    path: str,
) -> None:
    with open(path, "wb") as f:
        f.write(MAGIC)
        f.write(struct.pack("<I", VERSION))

        doc_ids = sorted(doc_lengths.keys())
        f.write(struct.pack("<I", len(doc_ids)))
        for doc_id in doc_ids:
            f.write(struct.pack("<II", doc_id, doc_lengths[doc_id]))

        directory: dict[str, tuple[int, int]] = {}
        for term, postings in term_postings.items():
            start_offset = f.tell()

            block = bytearray()
            block += struct.pack("<I", len(postings))
            for doc_id, positions in postings.items():
                block += struct.pack("<I", doc_id)
                block += struct.pack("<I", len(positions))
                for pos in positions:
                    block += struct.pack("<I", pos)

            f.write(bytes(block))
            directory[term] = (start_offset, len(block))

        directory_offset = f.tell()
        f.write(struct.pack("<I", len(directory)))
        for term, (offset, length) in directory.items():
            term_bytes = term.encode("utf-8")
            f.write(struct.pack("<H", len(term_bytes)))
            f.write(term_bytes)
            f.write(struct.pack("<QI", offset, length))

        f.write(struct.pack("<Q", directory_offset))

class MmapIndexReader:
    def __init__(self, path: str) -> None:
        self._file = open(path, "rb")
        self._mmap = mmap.mmap(self._file.fileno(), 0, access=mmap.ACCESS_READ)
        self._doc_lengths: dict[int, int] = {}
        self._directory: dict[str, tuple[int, int]] = {}
        self._load_header_and_directory()

    def _load_header_and_directory(self) -> None:
        data = self._mmap

        if data[0:4] != MAGIC:
            raise ValueError("Not a valid mmap index file (bad magic bytes)")

        offset = 4
        (version,) = struct.unpack_from("<I", data, offset)
        offset += 4
        if version != VERSION:
            raise ValueError(f"Unsupported mmap index format version: {version}")

        (num_docs,) = struct.unpack_from("<I", data, offset)
        offset += 4
        for _ in range(num_docs):
            doc_id, length = struct.unpack_from("<II", data, offset)
            offset += 8
            self._doc_lengths[doc_id] = length

        (directory_offset,) = struct.unpack_from("<Q", data, len(data) - 8)

        pos = directory_offset
        (num_terms,) = struct.unpack_from("<I", data, pos)
        pos += 4
        for _ in range(num_terms):
            (term_len,) = struct.unpack_from("<H", data, pos)
            pos += 2
            term = data[pos : pos + term_len].decode("utf-8")
            pos += term_len
            block_offset, block_length = struct.unpack_from("<QI", data, pos)
            pos += 12
            self._directory[term] = (block_offset, block_length)

    def document_length(self, doc_id: int) -> int:
        return self._doc_lengths.get(doc_id, 0)

    @property
    def document_count(self) -> int:
        return len(self._doc_lengths)

    @property
    def vocabulary_size(self) -> int:
        return len(self._directory)

    def get_postings(self, term: str) -> dict[int, list[int]]:
        if term not in self._directory:
            return {}

        offset, length = self._directory[term]
        block = self._mmap[offset : offset + length]

        postings: dict[int, list[int]] = {}
        pos = 0
        (num_postings,) = struct.unpack_from("<I", block, pos)
        pos += 4

        for _ in range(num_postings):
            (doc_id,) = struct.unpack_from("<I", block, pos)
            pos += 4
            (num_positions,) = struct.unpack_from("<I", block, pos)
            pos += 4
            positions = list(struct.unpack_from(f"<{num_positions}I", block, pos))
            pos += 4 * num_positions
            postings[doc_id] = positions

        return postings

    def close(self) -> None:
        self._mmap.close()
        self._file.close()

    def __enter__(self) -> "MmapIndexReader":
        return self

    def __exit__(self, *args) -> None:
        self.close()