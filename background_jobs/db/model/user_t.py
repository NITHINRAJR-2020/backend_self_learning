from db.database import base
from sqlalchemy import String , Column , Integer

class User(base):
    __tablename__= "user"
    id = Column(Integer , primary_key = True)
    name = Column(String)
    age = Column(Integer)