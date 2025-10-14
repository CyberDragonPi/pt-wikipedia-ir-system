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

    def run_tokenizer(self):
        # self.logger.info(f"Tokenizer initialized")
        return
