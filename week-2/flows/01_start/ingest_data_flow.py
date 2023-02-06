import pandas as pd
import os
import argparse
from sqlalchemy import create_engine
from time import time
from prefect import flow, task

def parquet_to_csv(parquet_file, csv_file):
    df = pd.read_parquet(parquet_file, engine = 'pyarrow')
    df.to_csv(csv_file, index=False)

@task(log_prints=True, retries=3)
def ingest(csv_file, table_name, engine, chunksize=100000):
    df_iter = pd.read_csv(csv_file, iterator=True, chunksize=chunksize)
    run = True
    while run:
        try:
            t_start = time()
            df = next(df_iter)
            df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
            df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])
            df.to_sql(name=table_name, con=engine, if_exists='append')
            t_end = time()
            print(f'inserted another chunk, took {t_end-t_start:.3f} seconds')
        except Exception:
            run = False

@flow(name='Ingest Data')
def main_flow():
    user = 'root'
    password = 'root'
    host = 'localhost'
    port = '5432'
    db = 'ny_taxi'
    table_name = 'yellow_taxi_trips'
    url = 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2021-01.parquet'
    parquet_file = 'output.parquet'
    csv_file = 'output.csv'
    os.system(f'wget {url} -O {parquet_file}')
    parquet_to_csv(parquet_file, csv_file)
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
    engine.connect()
    ingest(csv_file, table_name, engine)
    

if __name__ == '__main__':
    main_flow()
