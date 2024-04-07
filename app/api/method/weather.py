from app.api.method.conversion import mapToGrid
import datetime
import requests
import xmltodict
import json
import pandas as pd

def weather_info(lat, lon):
    lat = float(lat)
    lon = float(lon)
    nx, ny = mapToGrid(lat,lon)

    now = datetime.datetime.now()
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst?'

    service_keys = [
        'vInQMBs2Q5ZUB+OPHqTYO+p6UykITwbgNyLp0H489aSt2CSwGtx8/IVwHK4D6ljqmcTxH0uL5Cq9hRML986wNA==',
        'vInQMBs2Q5ZUB%2BOPHqTYO%2Bp6UykITwbgNyLp0H489aSt2CSwGtx8%2FIVwHK4D6ljqmcTxH0uL5Cq9hRML986wNA%3D%3D'
    ]
    success = False

    for service_key in service_keys:
        params = {
            'serviceKey': service_key,
            'pageNo': '1',
            'numOfRows': '1000',
            'dataType': 'XML',
            'base_date': now.strftime("%Y%m%d"),
            'base_time': '0500',
            'nx': nx,
            'ny': ny
        }
        with requests.Session() as session:
            response = session.get(url, params=params)
            xmlData = response.text
            jsonStr = json.dumps(xmltodict.parse(xmlData), indent=4)
            data = json.loads(jsonStr)            
            if data['response']['header']['resultCode'] == '00':
                success = True  # 요청 성공
                break  # 성공시 반복 중단
            else :
                print(f"Error: The API call failed with status code {response.status_code} and service key {service_key}")
    if success:
        df = pd.DataFrame(data['response']['body']['items']['item'])

        result_df = df.pivot(index=['fcstDate', 'fcstTime'], columns='category', values='fcstValue').reset_index()
        result_df = result_df.drop(['SNO','TMN','TMX','UUU','VVV','VEC'], axis=1)
        result_df.columns = ['date','time','precipitation','precip_probability','precip_type','humidity','sky_condition','temperature','wave_height','wind_speed']

        result_df['date'] = pd.to_datetime(result_df['date'], format='%Y%m%d').dt.strftime('%Y년 %m월 %d일')
        result_df['time'] = pd.to_datetime(result_df['time'], format='%H%M').dt.strftime('%H시')
        result_df['precipitation'] = result_df['precipitation'].replace('강수없음', '0').apply(lambda x: x + 'mm' if not x.endswith('mm') else x)
        result_df['precip_probability'] = result_df['precip_probability'].apply(lambda x: x + '%' if not x.endswith('%') else x)
        result_df['humidity'] = result_df['humidity'].apply(lambda x: x + '%' if not x.endswith('%') else x)
        result_df['temperature'] = result_df['temperature'].apply(lambda x: x + '℃' if not x.endswith('%') else x)
        result_df['wave_height'] = result_df['wave_height'].apply(lambda x: x + 'mm' if not x.endswith('%') else x)
        result_df['wind_speed'] = result_df['wind_speed'].apply(lambda x: x + 'm/s' if not x.endswith('%') else x)

        sky_condition_mapping = {
        '1': '맑음',
        '3': '구름많음',
        '4': '흐림'
        }
        rain_condition_mapping = {
            '0': '없음',
            '1': '비',
            '2': '비/눈',
            '3': '눈',
            '4': '소나기'
        }
        result_df['sky_condition'] = result_df['sky_condition'].map(sky_condition_mapping)
        result_df['precip_type'] = result_df['precip_type'].map(rain_condition_mapping)
        result_df['weather_condition'] = result_df.apply(lambda row: row['sky_condition'] if row['precip_type'] == '없음' else row['precip_type'], axis=1)
        result_df = result_df.drop(['sky_condition','precip_type'], axis=1)
    
        weather_condition_mapping = {
            '맑음':'<i class="bi bi-brightness-high"></i>',
            '구름많음':'<i class="bi bi-cloud"></i>',
            '흐림':'<i class="bi bi-cloud-haze2"></i>',
            '비':'<i class="bi bi-cloud-rain"></i>',
            '비/눈':'<i class="bi bi-cloud-sleet"></i>',
            '눈':'<i class="bi bi-cloud-snow"></i>',
            '소나기':'<i class="bi bi-cloud-drizzle"></i>'
        }
        result_df['weather_condition_icon'] = result_df['weather_condition'].map(weather_condition_mapping)        
        
        return result_df
    else:
        print("All API calls failed.")
        return None

