import json
import os
import gc
import psutil
import time
import pyarrow.dataset as ds

from sapien.core.tokenizer import Tokenizer


class Indexer:
    def __init__(
        self,
        file_path: str,
        min_term_freq: int = 1,
        output_directory: str = "output",
        forward_index: bool | int = False,
        inverted_format: str = "json",
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
        os.makedirs(self.output_directory, exist_ok=True)
        self.forward_index = forward_index
        self.inverted_format = inverted_format
        self.current_doc_id = 0
        self.spimi_block_id = 0
        self.spimi_block: dict[str, list[tuple[int, int]]] = dict()
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
            "stopwords": stopwords,
        }
        self.tokenizer = Tokenizer(**tokenizer_params)
        self.current_process = psutil.Process(os.getpid())
        return


    def output_configuration(self) -> str:
        indexer_configs = (
            f"Configuration:\n"
            f"  · Min term frequency: {self.min_term_freq}\n"
            f"  · Output directory: {self.output_directory}\n"
            f"  · Inverted index format: {self.inverted_format}\n"
            f"  · Forward index: {'enabled' if self.forward_index else 'disabled'}\n"
        )
        tokenizer_configs = self.tokenizer.output_configuration()
        return indexer_configs + tokenizer_configs


    def store_metadata(self):
        metadata_dict: dict[str, str] = dict()
        pass



    def create_index(self, batch_size: int = 1000, only_merge: bool = False) -> None:
        print(self.output_configuration())
        time.sleep(5)
        if self.forward_index:
            # self.create_forward_index(batch_size)
            pass
        else:
            if not only_merge:
                self.create_inverted_index(batch_size)

    """def create_forward_index(self, batch_size: int):
        dataset: ds.FileSystemDataset = ds.dataset(self.file_path, format="arrow")  # type: ignore
        current_id: int = 0
        spimi_block_id: int = 0
        spimi_block = {}

        for batch in dataset.to_batches(batch_size=batch_size):
            title_column = batch.column("title")  # type: ignore
            text_column = batch.column("text")  # type: ignore

            title_list = [str(t) for t in title_column.to_pylist() if t is not None]  # type: ignore
            text_list = [str(t) for t in text_column.to_pylist() if t is not None]  # type: ignore

            for title, text in zip(title_list, text_list):
                if not text.rstrip():
                    continue

                text_tokens: list[str] = self.tokenizer.tokenize(text)
                title_tokens: list[str] = self.tokenizer.tokenize(title)

                current_id += 1"""

    def create_inverted_index(self, batch_size: int, batches_to_flush: int = 40):
        dataset: ds.FileSystemDataset = ds.dataset(self.file_path, format="arrow")
        current_batch = 0
        batches_counter = 0

        for batch in dataset.to_batches(batch_size=batch_size):
            num_rows = batch.num_rows
            for i in range(num_rows):
                text = batch["text"][i].as_py()
                if not text.strip():
                    continue

                tokens = self.tokenizer.tokenize(text)

                term_freqs: dict[str, int] = dict()
                for token in tokens:
                    term_freqs[token] += 1

                for token, freq in term_freqs.items():
                    self.spimi_block[token].append((self.current_doc_id, freq))

                self.current_doc_id += 1

            rss_memory_mb = self.current_process.memory_info().rss / (1024 * 1024)
            if rss_memory_mb > 1600 or batches_counter == batches_to_flush:
                self.flush_block()
                batches_counter = 0

            batches_counter += 1
            print(f"Processed batch {current_batch}")
            current_batch += 1

            del batch
            gc.collect()

        self.flush_block()


    def flush_block(self):
        if not self.spimi_block:
            return
        sorted_terms = sorted(self.spimi_block.items())
        block_path = os.path.join(self.output_directory, f"block_{self.spimi_block_id}.json")
        with open(block_path, "w") as f:
            for token, postings in sorted_terms:
                f.write(json.dumps({token: postings}) + "\n")

        with open(self.block_paths_file, "a") as paths_file:
            paths_file.write(block_path + "\n")

        self.spimi_block.clear()
        self.spimi_block_id += 1
        del sorted_terms
        time.sleep(0.05) 
        gc.collect()
