from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class EmailServices(Base):
    __tablename__ = 'EmailServices'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    client_id = Column(String)
    client_secret = Column(String)

    def __init__(self, **p):
        self.name = p['name']
        self.client_id = p['client_id']
        self.client_secret = p['client_secret']

    def __str__(self):
        return self.name