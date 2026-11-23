from db.database import base
from sqlalchemy import Column , String , Integer

class Product(base):
    __tablename__= "product"
    id = Column(String , primary_key=True)
    name = Column(String)
    quantity = Column(Integer)


