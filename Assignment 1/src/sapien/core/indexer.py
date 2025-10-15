import logging

import pyarrow.dataset as ds

from sapien.core.tokenizer import Tokenizer


class Indexer:
    def __init__(
        self,
        file_path: str,
        min_term_freq: int = 1,
        output_directory: str = "./output",
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
        self.logger = logging.getLogger(__name__)
        # najjednostavnije je napraviti logger tako da se samo svakom objektu da njegov vlastiti

        # --- parametri samog indexera---
        self.file_path = file_path
        self.min_term_freq = min_term_freq
        self.output_directory = output_directory
        self.forward_index = forward_index
        self.inverted_format = inverted_format

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

    def create_index(self, batch_size: int = 1000) -> None:
        if self.forward_index:
            # self.create_forward_index(batch_size)
            pass
        else:
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

    def create_inverted_index(self, batch_size: int) -> None:
        dataset: ds.FileSystemDataset = ds.dataset(self.file_path, format="arrow")  # type: ignore
        current_id: int = 0
        # spimi_block_id: int = 0
        # spimi_block: Dict[str, List[Posting]] = {}

        for batch in dataset.to_batches(batch_size=batch_size):
            title_column = batch.column("title")  # type: ignore
            text_column = batch.column("text")  # type: ignore

            title_list = [str(t) for t in title_column.to_pylist() if t is not None]  # type: ignore
            text_list = [str(t) for t in text_column.to_pylist() if t is not None]  # type: ignore

            for title, text in zip(title_list, text_list):
                if not text.rstrip():
                    continue  # prazan string

                title += ""
                
                # za test samo ispis prvog dokuemnta
                if current_id == 0:
                    print("Title:", title)
                    print("Text:", text[:500], "...")  # prvih 500 znakova

                title_tokens = self.tokenizer.tokenize(title)
                text_tokens = self.tokenizer.tokenize(text)
                
                print("Title tokens:", title_tokens)
                print("Text tokens:", text_tokens[:50], "...")


                return # za test samo 
            
                # doc_id = current_id
                current_id += 1
