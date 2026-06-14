import os
from sqlalchemy import create_engine
import pandas as pd
import logging
import time

# configuration of activities 
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
# engine creation for database connection
engine = create_engine(
    "mysql+pymysql://root:suyog123poudel@localhost/company_db"
)

# save to sql without delay function
def save_to_sql(table_name,df):
    df.to_sql(
    name=table_name,
    con=engine,
    if_exists="replace",   
    index=False,
    chunksize=100000,
    method="multi"
    )
    print(f"Data inserted {table_name}")
    logging.info(f"Data inserted successfully of file  {table_name}")

#read all the files from the folder data
def read_files():
    start = time.time()
    files = os.listdir("data")
    for file in files:
        if ".csv" in file:
            print(f"Reading {file} ")
            table_name = file.split(".")[0]
            df = pd.read_csv(f"data/{file}")
            # save_to_sql(table_name,df)     # Faster insertion without delay but gives problem database overload
            # save_to_sql_delay(table_name,df,engine) # slower but restrict database overload with sleep function
    end = time.time()   
    total_time = (end-start)/60
    logging.info("\n"+"-------------INSERTION COMPLETED --------------")
    logging.info(f"Total Time for insertion is {total_time} minutes")


# Saves csv data to sql with 1.5s delay to protect database overload
def save_to_sql_delay(table_name, df, engine):
    chunk_size = 20000
    total_rows = len(df)

    for i in range(0, total_rows, chunk_size):
        chunk = df.iloc[i:i+chunk_size]

        chunk.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace" if i == 0 else "append",
            index=False,
            method="multi"
        )

        print(f"Inserted rows: {min(i + chunk_size, total_rows)} / {total_rows}")
        logging.info(f"Inserted up to row {min(i + chunk_size, total_rows)} in {table_name}")

        time.sleep(1.5)  # pause to avoid DB overload

    print(f"Data inserted successfully into {table_name}")
    logging.info(f"Completed insertion for table {table_name}")



if __name__ == "__main__":
    read_files()