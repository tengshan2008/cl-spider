from typing import Dict, Text


class Spider:
    def __init__(self, headers: Dict[Text, Text] = None) -> None:
        if headers is None:
            self.headers = {
                'User-Agent': ''
            }
        else:
            self.headers = headers
