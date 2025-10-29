from typing import Union
from collections import defaultdict


Offset = tuple[int, int]
Annotations = Union[dict[str, list[Offset]], defaultdict[list[Offset]]]