class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.is_end_of_word: bool = False

class Trie:
    def __init__(self) -> None:
        self._root = TrieNode()
        self._word_count = 0

    def insert(self, word: str) -> None:
        if not word:
            return
        node = self._root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]

        if not node.is_end_of_word:
            node.is_end_of_word = True
            self._word_count += 1

    def _find_node(self, prefix: str) -> TrieNode | None:
        node = self._root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def search(self, word: str) -> bool:
        node = self._find_node(word)
        return node is not None and node.is_end_of_word

    def starts_with(self, prefix: str) -> bool:
        return self._find_node(prefix) is not None

    def autocomplete(self, prefix: str, limit: int | None = None) -> list[str]:
        start_node = self._find_node(prefix)
        if start_node is None:
            return []

        results: list[str] = []
        self._collect_words(start_node, prefix, results, limit)
        return results

    def _collect_words(
        self, node: TrieNode, path: str, results: list[str], limit: int | None
    ) -> None:
        if limit is not None and len(results) >= limit:
            return
        if node.is_end_of_word:
            results.append(path)
        for char, child in node.children.items():
            if limit is not None and len(results) >= limit:
                return
            self._collect_words(child, path + char, results, limit)

    def delete(self, word: str) -> bool:
        if not self.search(word):
            return False

        self._delete_recursive(self._root, word, 0)
        self._word_count -= 1
        return True

    def _delete_recursive(self, node: TrieNode, word: str, depth: int) -> bool:
        if depth == len(word):
            node.is_end_of_word = False
            return len(node.children) == 0

        char = word[depth]
        child = node.children[char]
        should_prune_child = self._delete_recursive(child, word, depth + 1)

        if should_prune_child:
            del node.children[char]

        return len(node.children) == 0 and not node.is_end_of_word

    def __len__(self) -> int:
        return self._word_count

    def __contains__(self, word: str) -> bool:
        return self.search(word)