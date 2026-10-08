import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# read csv file
script_dir = os.path.dirname(os.path.abspath(__file__))
csv_file = os.path.join(script_dir, '..', 'shop-product-catalog.csv')
data = pd.read_csv(csv_file)

# connect to mysql
db_connection = mysql.connector.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'shopai')
)

cursor = db_connection.cursor()

# upload data to the table
sql = """
    INSERT INTO products (ProductID, ProductName, ProductBrand, Gender, Price, Description, PrimaryColor)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
"""
records = [tuple(row) for row in data.itertuples(index=False)]
cursor.executemany(sql, records)


db_connection.commit()

cursor.close()
db_connection.close()