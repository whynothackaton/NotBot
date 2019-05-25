from dataclasses import dataclass
import json


@dataclass(order=True)
class Action:
    type: str = 'Text'
    label: str = ""
    playloads: str = ""

    def toJSON(self):
        return json.dumps(self, default=lambda dic: dic.__dict__)

    def fromJSON(self, json_str):
        self.__dict__ = json.loads(json_str)