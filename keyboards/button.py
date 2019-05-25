from action import Action
from dataclasses import dataclass
import json


@dataclass(order=True)
class Button():
    color: str = 'primary'
    action: object = Action(type='Text')

    def change_action(self, action):
        self.action = action

    def change_color(self, color):
        self.color = color

    def toJSON(self):
        return json.dumps(self, default=lambda dic: dic.__dict__)

    def fromJSON(self, json_str):
        self.__dict__ = json.loads(json_str)
