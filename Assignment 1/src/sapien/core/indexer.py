import gc
import json
import os
import psutil
import glob
import heapq
import pyarrow.dataset as ds
from collections import defaultdict
from contextlib import ExitStack

from sapien.core.tokenizer import Tokenizer



class Indexer:
    def __init__(
        self,
        file_path: str,
        min_term_freq: int = 5,
        output_directory: str = "output",
        separate_alphanumeric: bool | int = False,
        remove_numbers: bool | int = False,
        remove_URLs: bool | int = False,
        remove_emails: bool | int = False,
        min_token_length: int = 1,
        lowercase: bool | int = False,
        stemmer: bool | int = False,
        stopwords: bool | int = False,
    ):
        # najjednostavnije je napraviti logger tako da se samo svakom objektu da njegov vlastiti
        # --- parametri samog indexera---
        self.file_path = file_path
        self.min_term_freq = min_term_freq
        self.output_directory = output_directory
        self.inverted_format = "json"
        os.makedirs(self.output_directory, exist_ok=True)
        self.inverted_index = defaultdict(list)
        self.block_count = 0
        self.token_count = 0
        self.token_threshold = 5000000  
        self.total_tokens = 0

        self.doc_lengths = {}
        self.doc_count = 0
        self.doc_stats_path = os.path.join(self.output_directory, "doc_stats.jsonl")
        self.block_paths_file = os.path.join(self.output_directory, "block_paths.txt")

        # --- parametri tokenizera---
        tokenizer_params = {
            "separate_alphanumeric": separate_alphanumeric,
            "remove_numbers": remove_numbers,
            "remove_URLs": remove_URLs,
            "remove_emails": remove_emails,
            "min_token_length": min_token_length,
            "lowercase": lowercase,
            "stemmer": stemmer,
            "use_stopwords": stopwords,
        }
        self.tokenizer = Tokenizer(**tokenizer_params)
        self.current_process = psutil.Process(os.getpid())

        self.metadata = {
            "file_path": file_path,
            "min_term_freq": min_term_freq,
            "output_directory": output_directory,
            "inverted_format": "json",
            "separate_alphanumeric": bool(separate_alphanumeric),
            "remove_numbers": bool(remove_numbers),
            "remove_URLs": bool(remove_URLs),
            "remove_emails": bool(remove_emails),
            "min_token_length": min_token_length,
            "lowercase": bool(lowercase),
            "stemmer": bool(stemmer),
            "stopwords": bool(stopwords),
        }

    def output_configuration(self) -> str:
        indexer_configs = (
            f"Configuration:\n"
            f"  · Min term frequency: {self.min_term_freq}\n"
            f"  · Output directory: {self.output_directory}\n"
            f"  · Inverted index format: {self.inverted_format}\n"
        )
        tokenizer_configs = self.tokenizer.output_configuration()
        return indexer_configs + tokenizer_configs

    def store_metadata(self):
        path = os.path.join(self.output_directory, "metadata.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=4, ensure_ascii=False)


    def load_dataset(self) -> ds.FileSystemDataset:
        return ds.dataset(self.file_path, format="arrow")


    def add_document(self, doc_id: int, tokens: list[str]):
        """Add one documents tokens to the in-memory index"""
        term_freq = defaultdict(int)
        valid_tokens = 0

        for term in tokens:
            term_freq[term] += 1
            valid_tokens += 1
            self.total_tokens += 1

        self.doc_lengths[doc_id] = valid_tokens
        self.doc_count += 1
        with open(self.doc_stats_path, "a", encoding="utf-8") as stats_file:
            stats_file.write(json.dumps({"doc_id": doc_id, "length": valid_tokens}) + "\n")

        for term, freq in term_freq.items():
            self.inverted_index[term].append((doc_id, freq))
            self.token_count += 1

        process = psutil.Process()
        memory_limit = 2 * 1024 * 1024 * 1024
        mem_usage = process.memory_info().rss

        if self.token_count >= self.token_threshold or mem_usage > memory_limit * 0.8:
            self._write_block()
            self.token_count = 0


    def _write_block(self):
        """Writes one sorted block to a .jsonl file (one term per line)"""
        self.block_count += 1
        block_path = os.path.join(self.output_directory, f"{self.block_count}.jsonl")
        sorted_index = dict(sorted(self.inverted_index.items()))

        with open(block_path, "w", encoding="utf-8") as f:
            for term, postings in sorted_index.items():
                f.write(json.dumps({term: postings}) + "\n")

        print(
            f"SPIMI wrote block {self.block_count} "
            f"with {len(self.inverted_index)} terms, {block_path}"
        )
        del sorted_index
        self.inverted_index.clear()
        gc.collect()
        self.token_count = 0


    def finalize(self):
        """Flush any remaining in-memory index to disk"""
        if self.inverted_index:
            self._write_block()

        print("SPIMI indexing complete")

        avg_doc_length = self.total_tokens / self.doc_count if self.doc_count > 0 else 0

        metadata = {
            "doc_count": self.doc_count,
            "total_tokens": self.total_tokens,
            "avg_doc_length": avg_doc_length,
            "doc_stats_file": os.path.basename(self.doc_stats_path),
        }

        meta_path = os.path.join(self.output_directory, "documents_metadata.jsonl")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)

        print(f"Metadata saved to {meta_path}")
        print(f"Document stats written to {self.doc_stats_path}")


    def _clear_memory_before_merge(self):
        if hasattr(self, "inverted_index"):
            self.inverted_index.clear()
            del self.inverted_index
            self.inverted_index = defaultdict(list)
        
        if hasattr(self, "doc_lengths"):
            self.doc_lengths.clear()
            del self.doc_lengths
            self.doc_lengths = {}

        if hasattr(self, "tokenizer"):
            del self.tokenizer

        gc.collect()
        
        process = psutil.Process(os.getpid())
        print(f"Memory after clearing: {process.memory_info().rss / 1024**2:.2f} MB")
    

    def merge_blocks(self):
        self._clear_memory_before_merge()
        """Merge all intermediate .jsonl blocks into a single final index"""
        block_files = sorted(
            f
            for f in glob.glob(os.path.join(self.output_directory, "*.jsonl"))
            if not f.endswith(("final_index.jsonl", "doc_stats.jsonl", "metadata.jsonl", "documents_metadata.jsonl"))
        )

        if not block_files:
            print("No blocks to merge")
            return

        process = psutil.Process()
        memory_limit = 2 * 1024 * 1024 * 1024  # 2GB

        with ExitStack() as stack:
            block_handles = [
                stack.enter_context(open(path, encoding="utf-8")) for path in block_files
            ]
            block_iterators = [self._line_iterator(f) for f in block_handles]

            heap = []
            for block_id, iterator in enumerate(block_iterators):
                try:
                    term, postings = next(iterator)
                    heapq.heappush(heap, (term, postings, block_id))
                except StopIteration:
                    continue

            final_index_path = os.path.join(self.output_directory, "final_index.jsonl")
            temp_index_path = os.path.join(self.output_directory, "temp_index.jsonl")

            current_term = None
            current_postings = []
            term_count = 0

            with open(temp_index_path, "w", encoding="utf-8") as f:
                while heap:
                    mem_usage = process.memory_info().rss
                    if mem_usage > memory_limit * 0.9:
                        print(f"Memory usage high ({mem_usage / (1024 ** 2):.2f} MB), flushing...")

                    term, postings, block_id = heapq.heappop(heap)

                    if term == current_term:
                        current_postings.extend(postings)
                    else:
                        if current_term:
                            merged_postings = self._merge_postings(current_postings)
                            if len(merged_postings) >= self.min_term_freq:
                                f.write(json.dumps({current_term: merged_postings}) + "\n")
                                term_count += 1

                        current_term = term
                        current_postings = postings

                    try:
                        next_term, next_postings = next(block_iterators[block_id])
                        heapq.heappush(heap, (next_term, next_postings, block_id))
                    except StopIteration:
                        continue

                if current_term:
                    merged_postings = self._merge_postings(current_postings)
                    if len(merged_postings) >= self.min_term_freq:
                        f.write(json.dumps({current_term: merged_postings}) + "\n")
                        term_count += 1

        os.rename(temp_index_path, final_index_path)
        print(f"Merged {len(block_files)} blocks, {term_count} terms written to {final_index_path}")


    @staticmethod
    def _merge_postings(postings):
        """Combine duplicate (docID, freq) pairs, summing frequencies per docID"""
        merged = defaultdict(int)
        for doc_id, freq in postings:
            merged[doc_id] += freq
        return sorted(merged.items())


    @staticmethod
    def _line_iterator(file_handle):
        """Generator that yields (term, postings) pairs from a .jsonl block"""
        for line in file_handle:
            if not line.strip():
                continue
            data = json.loads(line)
            term, postings = next(iter(data.items()))
            yield term, postings
