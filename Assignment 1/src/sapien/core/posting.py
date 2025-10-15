from dataclasses import dataclass


@dataclass
class Posting:
    document_id: int
    positions: list[int]
