from pydantic import BaseModel

class Product(BaseModel):
    product_id : str
    p_name:str
    p_qty:int
