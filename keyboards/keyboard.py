from button import Button
from dataclasses import dataclass, field
import json
from typing import List


@dataclass(order=True)
class KeyBoard():
    one_time: bool = True
    buttons: List[Button] = field(default_factory=list)

    def add_button(self, button):
        self.buttons.append(button)

    def toJSON(self):
        return json.dumps(self, default=lambda dic: dic.__dict__)

    def fromJSON(self, json_str):
        self.__dict__ = json.loads(json_str)
