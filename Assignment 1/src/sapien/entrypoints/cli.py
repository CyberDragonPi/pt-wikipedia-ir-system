import argparse
import logging

from sapien.core.limit_memory import start_memory_monitor
from sapien.core.logging import setup_logging

setup_logging(logging.INFO)
start_memory_monitor(show_memory_updates=True)


def main():
    # TODO continue here
    parser = argparse.ArgumentParser(description="Sapien Indexer CLI")

    # basic arguments for the indexer
    parser.add_argument("file_path", type=str, help="Path to the file to index")
    parser.add_argument(
        "--min_term_freq", type=int, default=1, help="Minimum term frequency to store"
    )
    parser.add_argument(
        "--output_directory",
        type=str,
        default="./output",
        help="Directory to store generated files",
    )
    parser.add_argument(
        "--forward_index", action="store_true", help="Enable creation of forward index"
    )
    parser.add_argument(
        "--inverted_format",
        type=str,
        choices=["json", "csv"],
        default="json",
        help="Output format of inverted index",
    )

    # tokenizer arguments
    parser.add_argument(
        "--separate_alphanumeric", action="store_true", help="Separate alphanumeric tokens"
    )
    parser.add_argument(
        "--remove_numbers", action="store_true", help="Remove tokens that only have numbers"
    )
    parser.add_argument(
        "--min_token_length", type=int, default=1, help="Minimum token length to store"
    )
    parser.add_argument(
        "--lowercase", action="store_true", help="Convert tokens to lowercase before creating index"
    )
    parser.add_argument("--stemmer", action="store_true", help="Enable stemming")
    parser.add_argument("--stopwords", action="store_true", help="Remove stopwords")

    _ = parser.parse_args()


if __name__ == "__main__":
    main()
