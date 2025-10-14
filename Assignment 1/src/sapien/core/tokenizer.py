import re


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
        self.separate_alphanumeric = separate_alphanumeric
        self.remove_numbers = remove_numbers
        self.remove_URLs = remove_URLs
        self.remove_emails = remove_emails
        self.min_token_length = min_token_length
        self.lowercase = lowercase
        self.stemmer = stemmer
        self.stopwords = stopwords
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

    def tokenize(self, text: str):
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

        cleaned_tokens = []
        for t in tokens:
            # remove numbers
            if self.remove_numbers and t.isdigit():
                continue

            # separate alphanumeric
            if self.separate_alphanumeric:
                characters = set(t)
                # if there are both letters and digits
                if any(c.isalpha() for c in characters) and any(c.isdigit() for c in characters):
                    ## splitanje brojeva i slova
                    splitted = re.findall(r"\D+|\d+", t)

        return
