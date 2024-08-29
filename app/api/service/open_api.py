import os
import requests
from app.config.config import *
from urllib.parse import urlencode
import psycopg2
from psycopg2 import extras
from loguru import logger
import xml.etree.ElementTree as ET
import pandas as pd
import json
import certifi
import ssl


class OpenApi(object):
    

    def __init__(self):
        pass

    # excel로 변환
    def to_excel(self, id: str, parameter: str):
        
        try:
            open_api_info = get_open_api_info(id)

            api_key = open_api_info[0][0]
            base_url = open_api_info[0][1]
            type = open_api_info[0][2]

            params = {
                "serviceKey": api_key
            }

            if parameter is not None:
                additional_params = json.loads(parameter)
                params.update(additional_params)

            url = f"{base_url}?{urlencode(params)}"
            
            #ssl._create_default_https_context = ssl._create_unverified_context

            headers = {
               # "Content-type": "application/json",
               # "Accept": "application/json"  # JSON 응답을 원할 경우 주석 해제 
                "accept": "*/*"
            }

            response = requests.get(url, headers=headers)
            print(f"Response code: {response.status_code}") 

            if response.status_code >= 200 and response.status_code <= 300:
                print(response.text)
            else:
                print(response.text)

            if type == "json":
                json_to_excel(response.text, id)
            
            if type == "xml":
                xml_to_excel(response.text, id)

            return "sucess"

        except Exception as e:
            print(e)
            return e

def json_to_excel(json_data: str, file_name: str):

    data = json.loads(json_data)
    # XML 데이터 파싱
    items = data["response"]["body"]["items"]["item"]

    df = pd.DataFrame(items)

    # 엑셀 파일로 저장
    save_path = os.path.join(excel_complete_file_dir, f"{file_name}.xlsx")
    df.to_excel(save_path, index=False)

def xml_to_excel(xml_data:str, file_name: str):
    # XML 데이터 파싱
    root = ET.fromstring(xml_data)

    # 데이터를 저장할 리스트
    data = []

    # item 요소를 찾아서 데이터 추출
    for item in root.findall(".//row"):
        item_data = {}
        for child in item:
            if child.tag == "description":
                item_data[child.tag] = ET.tostring(child, encoding='unicode', method='text').strip()
            else:
                item_data[child.tag] = child.text if child.text is not None else ""
        data.append(item_data)

    # 데이터프레임 생성
    df = pd.DataFrame(data)

    # 엑셀 파일로 저장
    save_path = os.path.join(excel_complete_file_dir, f"{file_name}.xlsx")
    df.to_excel(save_path, index=False)

def get_open_api_info(id: str):

    try:
        connection, cursor = get_db_connection()

        query = f"SELECT api_key, base_url, type FROM public.open_api_info where id='{id}';"
        cursor.execute(query)
        results = cursor.fetchall()
        
        #open_api_info = [row for row in results]

    except Exception as e:
        logger.error(f"Failed to execute query. message:{e}")

    finally:
        cursor.close()
        connection.close()
    
    return results
      
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