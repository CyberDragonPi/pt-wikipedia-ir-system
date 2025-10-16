import re
from typing import Optional, Set

from nltk.stem.snowball import SnowballStemmer


class Tokenizer:
    def __init__(
        self,
        separate_alphanumeric: bool | int = False,
        remove_numbers: bool | int = False,
        remove_URLs: bool | int = False,
        remove_emails: bool | int = False,
        min_token_length: int = 1,
        lowercase: bool | int = False,
        stemmer: bool | int = False,
        stopwords: bool | int = False,
    ):
        self.separate_alphanumeric: bool | int = separate_alphanumeric
        self.remove_numbers: bool | int = remove_numbers
        self.remove_URLs: bool | int = remove_URLs
        self.remove_emails: bool | int = remove_emails
        self.min_token_length: int = min_token_length
        self.lowercase: bool | int = lowercase
        self.stemmer: bool | int = stemmer
        self.stopwords: bool | int = stopwords
        self.stemmer_pt: Optional[SnowballStemmer] = None
        self.stopwords_pt: Set[str] = set()

        # defining stemmer
        if self.stemmer:
            self.stemmer_pt = SnowballStemmer("portuguese")

        # defining stopwords
        if self.stopwords:
            self.stopwords_pt = set(stopwords.words("portuguese"))

        return

    def output_configuration(self) -> str:
        configuration = (
            f"  · Tokenizer configuration:\n"
            f"     · Separate alphanumeric:"
            f"{'enabled' if self.separate_alphanumeric else 'disabled'}\n"
            f"     · Remove numbers: {'enabled' if self.remove_numbers else 'disabled'}\n"
            f"     · Remove URLs: {'enabled' if self.remove_URLs else 'disabled'}\n"
            f"     · Remove emails: {'enabled' if self.remove_emails else 'disabled'}\n"
            f"     · Min token length: {self.min_token_length}\n"
            f"     · Lowercase: {'enabled' if self.lowercase else 'disabled'}\n"
            f"     · Stemmer: {'enabled' if self.stemmer else 'disabled'}\n"
            f"     · Stopwords: {'enabled' if self.stopwords else 'disabled'}\n"
        )
        return configuration

    def tokenize(self, text: str) -> list[str]:
        # lowercase
        if self.lowercase:
            text = text.lower()

        # remove URL's
        if self.remove_URLs:
            text = re.sub(r"https?://\S+|www\.\S+", "", text)

        # remove e-mails
        if self.remove_emails:
            text = re.sub(r"\S+@\S+", "", text)

        # basic tokenization
        # keep every word that is made of letters and numbers
        # re.UNICIDE - letters from other languages are included
        tokens = re.findall(r"\w+", text, flags=re.UNICODE)

        # separate alphanumeric
        if self.separate_alphanumeric:
            new_tokens = []
            for t in tokens:
                splitted = re.findall(r"\D+|\d+", t)  # abc123 → ["abc", "123"]
                new_tokens.extend(splitted)
            tokens = new_tokens

        # remove numbers
        if self.remove_numbers:
            tokens = [t for t in tokens if not t.isdigit()]

        # check token length (so expensive operations like stemming arent performed if they shouldnt)
        tokens = [t for t in tokens if len(t) >= self.min_token_length]

        # remove stopwords
        if self.stopwords and self.stopwords_pt is not None:
            tokens = [t for t in tokens if t not in self.stopwords_pt]

        # stemming
        if self.stemmer and self.stemmer_pt is not None:
            tokens = [self.stemmer_pt.stem(t) for t in tokens]

        # check token length again
        tokens = [t for t in tokens if len(t) >= self.min_token_length]

        return tokens
