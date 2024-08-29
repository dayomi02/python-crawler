from app.util.constants import *

import re
import pandas as Dataframe
from pyproj import Proj, Transformer
from loguru import logger


# standard_meta에 대한 행만 남기고 나머지 삭제
# 위도 경도 변환
# etc, description 통합
def preprocess_data(meta: dict, df: Dataframe):
    # etc, description 통합 
    meta_desc = meta[DESCRIPTION]
    if meta_desc is not None and meta_desc != '' and '@/@' in meta_desc:
        split_meta_desc = re.split(r'@/@', meta_desc)
        df[meta_desc] = df.apply(lambda row: '\n'.join(row[split_meta_desc].astype(str)), axis=1)

    meta_etc = meta[ETC]
    if meta_etc is not None and meta_etc != '' and '@/@' in meta_etc:
        split_meta_etc = re.split(r'@/@', meta_etc)
        df[meta_etc] = df.apply(lambda row: '\n'.join(row[split_meta_etc].astype(str)), axis=1)

    # 위도, 경도(x축, y축) 변환
    latitude = meta[LATITUDE]
    longitude = meta[LONGITUDE]

    if latitude is not None and longitude is not None and latitude != '' and longitude != '':
        for index, row in df.iterrows():
            row_lat = row[latitude]
            row_lon = row[longitude]
            # latitude에 ", "로 위도&경도가 같이 들어있는 경우 처리
            if type(row_lat) != float and ', ' in row_lat:
                row_lat, row_lon = row_lat.split(', ')
            try:
                # 문자열이 숫자로 변환 가능한지 확인
                lat = float(row_lat)
                lon = float(row_lon)
            except (ValueError, TypeError):
                # 형 변환 실패 시 다음 행으로 넘어감
                # logger.info(f"위도, 경도 변환 실패 !!! source: {meta[MONGO_COLLECTION_NAME]}, value: {row_lat}/{row_lon}")
                # continue
                # 위도&경도 형태 처리 (N37.334846&E127.930154)
                lat, lon = parse_lat_lon(row_lat, row_lon)
                
                new_longitude, new_latitude = determine_coordinate_type(lat, lon)
                df.loc[index, latitude] = new_latitude
                df.loc[index, "longitude"] = new_longitude

                if meta[LONGITUDE] != LONGITUDE:
                     meta[LONGITUDE] = LONGITUDE

                continue
            new_longitude, new_latitude = determine_coordinate_type(lat, lon)
            df.loc[index, latitude] = new_latitude
            df.loc[index, longitude] = new_longitude

    # 필요 없는 열 삭제
    reverse_meta = {v: k for k, v in meta.items()}
    columns_to_keep = [col for col in df.columns if col in reverse_meta]
    df = df[columns_to_keep]

    # 열 이름 치환
    # df.columns = [reverse_meta.get(col, col) for col in df.columns]
    # print(df.columns)

    return df

def determine_coordinate_type(value1, value2):
    """
    주어진 두 값이 위도/경도인지 X/Y 좌표인지 결정합니다.

    Args:
    value1 (float): 첫 번째 좌표 값 (위도 또는 X 좌표).
    value2 (float): 두 번째 좌표 값 (경도 또는 Y 좌표).

    Returns:
    float: atitude, longitude
    """
    # 위도와 경도의 범위 (WGS84 기준)
    LATITUDE_MIN, LATITUDE_MAX = -90, 90
    LONGITUDE_MIN, LONGITUDE_MAX = -180, 180
    
    # 좌표가 위도/경도 범위 내에 있는지 확인
    if LATITUDE_MIN <= value1 <= LATITUDE_MAX and LONGITUDE_MIN <= value2 <= LONGITUDE_MAX:
        return value1, value2
        # return "latitude_longitude"
    else:
        latitude, longitude = tm_to_wgs84(value1, value2)
        return latitude, longitude
        # return "xy_coordinates"


def tm_to_wgs84(x, y, tm_epsg='5186'):
    """
    TM 좌표계를 WGS84 (위도, 경도)로 변환합니다.

    Args:
    x (float): TM X 좌표 (동경).
    y (float): TM Y 좌표 (북위).
    tm_epsg (str): TM 좌표계의 EPSG 코드 (기본값은 '5186', Korea 2000 / Central Belt).

    Returns:
    tuple: 변환된 (위도, 경도).
    """
    # TM 좌표계 정의
    tm_proj = Proj(init=f'epsg:{tm_epsg}')
    # WGS84 좌표계 정의
    wgs84_proj = Proj(init='epsg:4326')

    # Transformer 사용하여 좌표 변환
    transformer = Transformer.from_proj(tm_proj, wgs84_proj)
    lon, lat = transformer.transform(x, y)

    return lat, lon


def parse_lat_lon(lat_str, lon_str):
    """
    문자열 형태의 위도와 경도를 실수 형태로 변환합니다.

    Args:
    lat_str (str): 위도 문자열 (예: 'N36.960756').
    lon_str (str): 경도 문자열 (예: 'E127.043367').

    Returns:
    tuple: 변환된 (위도, 경도).
    """
    # 위도와 경도의 방향과 값을 추출
    lat_dir = lat_str[0]  # 'N', 'S'
    lon_dir = lon_str[0]  # 'E', 'W'
    
    lat_value = float(lat_str[1:])
    lon_value = float(lon_str[1:])
    
    # 남위 또는 서경일 경우 음수로 변환
    if lat_dir == 'S':
        lat_value = -lat_value
    if lon_dir == 'W':
        lon_value = -lon_value
    
    return lat_value, lon_value