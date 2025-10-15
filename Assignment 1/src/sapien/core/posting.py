from dataclasses import dataclass
from typing import List


@dataclass
class Posting:
    document_id: int
    position: List[int]
