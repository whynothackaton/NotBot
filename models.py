from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class EmailServices(Base):
    __tablename__ = 'EmailServices'

    name = Column(String, primary_key=True)
    client_id = Column(String)
    client_secret = Column(String)

    def __init__(self, params):
        self.name = params['name']
        self.client_id = params['client_id']
        self.client_secret = params['client_secret']

    def __str__(self):
        return self.name
