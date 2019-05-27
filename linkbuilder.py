from dataclasses import dataclass


@dataclass(order=True)
class LinkBuilder():
    url: str
    client_id: str
    scope: str
    redirect_uri: str
    response_type: str
    state: str

    def get(self) -> str:
        link = self.url + '?' + ''.join([
            key + '=' + self.__dict__[key] + '&'
            for key in self.__dict__ if key != 'url'
        ])
        return link[0:-1]