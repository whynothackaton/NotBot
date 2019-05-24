from dataclasses import dataclass, field
import json


@dataclass(order=True)
class Message():
    sender_id: str = None
    sender: str = None
    recipient: str = None
    subject: str = None
    text: str = None
    keys = ['sender_id', 'sender', 'recipient', 'subject', 'text']
    occupancy: int = 0

    def toJSON(self):
        return json.dumps(self, default=lambda dic: dic.__dict__)

    def fromJSON(self, json_string):
        self.__dict__ = json.loads(json_string)

    def get_next_item(self):

        return self.keys[self.occupancy]

    def set_this_item(self, value):
        self.__dict__[self.keys[self.occupancy]] = value
        self.occupancy += 1

    def get_occupancy(self):
        return int(self.occupancy * (100 / len(self.keys)))


