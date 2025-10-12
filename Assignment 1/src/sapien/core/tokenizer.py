import logging


class Tokenizer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        return

    def run_tokenizer(self):
        self.logger.info("Tokenizer initialized")
