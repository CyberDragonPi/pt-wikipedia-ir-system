import logging

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
