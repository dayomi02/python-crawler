from app.config.config import *
from app.util.constants import *
from app.api.service.data_preprocessing import preprocess_data
from app.api.service.move_file import move_file_to_directory
from app.api.models.baseResponse import BaseResponse

import psycopg2
from psycopg2 import extras
from pymongo import MongoClient
from loguru import logger
import os
import glob
import pandas as pd


def main():
    message = "success"

    try:
            
        standard_meta_info = get_standard_meta_info()
        # logger.info(f"standard_meta_info:: {standard_meta_info}")

        standard_metas = get_standard_meta(', '.join(standard_meta_info))
        # logger.info(f"standard_meta:: {standard_metas}")

        for standard_meta in standard_metas:
            logger.info(f"standard_meta:: {standard_meta}")
            dict_meta = dict(zip(standard_meta_info, standard_meta))

            data = read_excel_file(meta=dict_meta, standard_meta=standard_meta)
            
            # logger.info(data)
            if len(data) > 0:
                save_to_mongo(standard_meta=standard_meta, data=data)
    except Exception as e:
        message = e
        
    return BaseResponse(result=message)

# standard_meta_info 조회
def get_standard_meta_info():
    try:
        connection, cursor = get_db_connection()

        query = "SELECT id, meta FROM public.standard_meta_info;"
        cursor.execute(query)
        results = cursor.fetchall()
        
        standard_meta_info = [row[1] for row in results]

    except Exception as e:
        logger.error(f"Failed to execute query. message:{e}")

    finally:
        cursor.close()
        connection.close()
    
    return standard_meta_info

# standard_meta 조회
def get_standard_meta(meta_info: str):
    try:
        connection, cursor = get_db_connection()

        query = f"SELECT {meta_info} FROM public.standard_meta;"
        cursor.execute(query)
        standard_meta = cursor.fetchall()

    except Exception as e:
        logger.error(f"Failed to execute query. message:{e}")

    finally:
        cursor.close()
        connection.close()
    
    return standard_meta

# excel 데이터 조회
def read_excel_file(meta: dict, standard_meta: tuple):
    type = "xlsx"
    
    if standard_meta[MONGO_COLLECTION_NAME] == "datagg_restaurants_best" or standard_meta[MONGO_COLLECTION_NAME] == "data_food_health"\
        or standard_meta[MONGO_COLLECTION_NAME] == "data_global_culture_show" or standard_meta[MONGO_COLLECTION_NAME] == "data_global_culture_festival"\
        or standard_meta[MONGO_COLLECTION_NAME] == "data_patriotic_zeal" :
        type = "xls"
    elif standard_meta[MONGO_COLLECTION_NAME] == "data_character" or standard_meta[MONGO_COLLECTION_NAME] == "data_historical_personality":
        type = "csv"
    
    if type == "xls":
        search_pattern = os.path.join(excel_file_dir, f"{standard_meta[MONGO_COLLECTION_NAME]}.xls")
    elif type == "csv":
        search_pattern = os.path.join(excel_file_dir, f"{standard_meta[MONGO_COLLECTION_NAME]}.csv")
    else:
        search_pattern = os.path.join(excel_file_dir, f"{standard_meta[MONGO_COLLECTION_NAME]}*.xlsx")
    file_paths = glob.glob(search_pattern)
    
    excel_data = []
    for file_path in file_paths:
        if type == "xls":
            df = pd.read_excel(file_path, engine='xlrd')  
        elif type == "csv":
            df = pd.read_csv(file_path, encoding='utf-8')
        else:
            df = pd.read_excel(file_path, engine='openpyxl')  
        
        preprocessed_df = preprocess_data(meta, df)
        json_data = preprocessed_df.to_dict(orient='records')  
        # excel_data.append(json_data)
        excel_data.extend(json_data)

        move_file_to_directory(file_path, excel_complete_file_dir)
    

    return excel_data

# mongo 저장
def save_to_mongo(standard_meta: tuple, data: list):
    try:
        client = MongoClient(mongo_url)

        db = client[mongo_database]
        collection = db[standard_meta[MONGO_COLLECTION_NAME]]

        documents = data
        # 배치 크기 설정
        batch_size = 1000
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            result = collection.insert_many(batch, ordered=False)
            print(f'Inserted {len(result.inserted_ids)} documents')

    except Exception as e:
        logger.error(f"Failed to save mongo. message:{e}")

    finally:
        client.close()


# db connection
def get_db_connection():
    connection = psycopg2.connect(
            host=pg_host,
            port=pg_port,
            database=pg_database,
            user=pg_user,
            password=pg_password
        )
    # cursor = connection.cursor()
    cursor = connection.cursor(cursor_factory=extras.DictCursor)


    return connection, cursor