import json
import math
from collections import defaultdict

from sapien.core.tokenizer import Tokenizer


class SearchEngine:
    def __init__(
        self,
        index_path: str = "output/final_index.jsonl",
        documents_stats_path: str = "output/doc_stats.jsonl",
        documents_metadata_path: str = "output/documents_metadata.jsonl",
        indexer_metadata_path: str = "output/metadata.jsonl",
    ):
        self.index_path = index_path
        self.documents_stats_path = documents_stats_path
        self.documents_metadata_path = documents_metadata_path
        self.indexer_metadata_path = indexer_metadata_path
        self.index = defaultdict(list)
        self.documents_lengths = {}
        self.document_count = 0
        self.average_document_length = 0
        self.total_tokens = 0
        self.tokenizer_metadata = {}

        # self.load_index()
        self.load_documents_stats()
        self.load_documents_metadata()
        self.load_indexer_metadata()

        self.tokenizer = Tokenizer(**self.tokenizer_metadata)

    def load_index(self):
        print(f"Loading index from {self.index_path}...")
        with open(self.index_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                term, postings = next(iter(data.items()))
                self.index[term] = postings

    def load_documents_stats(self):
        with open(self.documents_stats_path, encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                self.documents_lengths[data["doc_id"]] = data["length"]

    def load_documents_metadata(self):
        with open(self.documents_metadata_path, encoding="utf-8") as f:
            data = json.load(f)
            self.document_count = data.get("doc_count", 0)
            self.average_document_length = data.get("avg_doc_length", 0)
            self.total_tokens = data.get("total_tokens", 0)

    def load_indexer_metadata(self):
        with open(self.indexer_metadata_path, encoding="utf-8") as f:
            metadata = json.load(f)

            tokenizer_metadata = {
                "separate_alphanumeric": metadata.get("separate_alphanumeric", False),
                "remove_numbers": metadata.get("remove_numbers", False),
                "remove_URLs": metadata.get("remove_URLs", False),
                "remove_emails": metadata.get("remove_emails", False),
                "min_token_length": metadata.get("min_token_length", 1),
                "lowercase": metadata.get("lowercase", False),
                "stemmer": metadata.get("stemmer", False),
                "use_stopwords": metadata.get("stopwords", False),
            }

        self.tokenizer_metadata = tokenizer_metadata

    # reading postings for a given term from the index file
    def get_term_postings(self, term: str):
        print(f"Loading postings for term {term} from {self.index_path}...")
        with open(self.index_path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                data = json.loads(line)
                t, postings = next(iter(data.items()))
                if term == t:
                    return postings
            return []

    def search(self, query: str, top_k: int = 10, k: float = 1.2, b: float = 0.75) -> list[dict]:
        print(f"this is query before tokenization: {query}")
        tokens = self.tokenizer.tokenize(query)
        print(f"tokens: {tokens}")

        scores = {}  # bm25 score for each doc_id is stored here
        for token in tokens:
            postings = self.get_term_postings(token)
            if not postings:
                continue

            df = len(postings)  # in how many documents is the term
            idf = math.log(1 + (self.document_count - df + 0.5) / (df + 0.5))
            # ili math.log(self.document_count / df)
            # tako je u prezi, a svuda drugdje na internetu ovo nekomentirano ?

            for doc_id, tf in postings:
                doc_len = self.documents_lengths[doc_id]
                score = (
                    idf
                    * (tf * (k + 1))
                    / (tf + k * ((1 - b) + b * (doc_len / self.average_document_length)))
                )
                scores[doc_id] = scores.get(doc_id, 0) + score

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]

    def search_similar(self, document_id: int):
        pass
