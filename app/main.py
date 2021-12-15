from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import FastAPI,Response,status,HTTPException
from fastapi.params import  Body
from pydantic import BaseModel
import time

app = FastAPI()

class Product(BaseModel):
    name:str
    price:int
    is_sale:bool
    inventory:int


while True:
    try: 
        conn = psycopg2.connect(host= 'localhost', database= 'FastAPI', user= 'postgres', password= '12345', cursor_factory= RealDictCursor)
        cursor= conn.cursor()
        print ("Database connected successfully")
        break
    except Exception as error:
        print(error)
        time.sleep(2)    

@app.get('/products')
def get_product():
    cursor.execute(""" SELECT * FROM PRODUCTS""")
    prods = cursor.fetchall() 
    return {'data': prods}  

@app.get('/products/{id}')
def get_one_product(id : int):
    cursor.execute("""SELECT * from Products WHERE id = %s """, (str(id),))
    prod = cursor.fetchone() 
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Product with id= {id} not found in database")
    return {'data': prod}

@app.post('/products', status_code=status.HTTP_201_CREATED)
def create_product(prod:Product):
    cursor.execute(""" INSERT INTO PRODUCTS (name,price,is_sale,inventory) VALUES (%s,%s,%s,%s) RETURNING * """,
                                                        (prod.name,prod.price,prod.is_sale,prod.inventory))
    new_prod= cursor.fetchone()
    conn.commit()
    return {'data':new_prod}

@app.delete('/products/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id : int):
    cursor.execute(""" DELETE from products where id = %s RETURNING *""",(str(id),))
    prod = cursor.fetchone()
    conn.commit()
    if prod== None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Product with id= {id} not found in database")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put('/products/{id}')
def update_post(id:int, prods:Product):
    cursor.execute(""" UPDATE products SET name = %s, price= %s, is_sale= %s , inventory= %s where id= %s RETURNING *""",(prods.name,prods.price,prods.is_sale,prods.inventory,str(id)))
    prod = cursor.fetchone()
    conn.commit()
    if  not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"Product with id= {id} not found in database")
    return {'data': prod}    