import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from io import StringIO
import boto3

"""



"""

client_s3 = boto3.client('s3', region_name='us-east-1')
# s3.Bucket('paus-bucket').upload_file('/datasets/CVI_data_collector.csv', 'hello.txt')


def get_volatility_index():
    url = "https://www.investing.com/indices/crypto-volatility-index"
    content = requests.get(url)
    soup = BeautifulSoup(content.text, "lxml")
    div_min = soup.find('div', class_='min-w-0')
    price_div = div_min.find('div', class_='text-5xl/9 font-bold text-[#232526] md:text-[42px] md:leading-[60px]')

    return price_div.text


def get_CVI_dataset() -> pd.DataFrame:
    """Get CVI Dataset from AWS"""
    try:
        response = client_s3.get_object(Bucket='paus-bucket', Key='datasets/CVI_data_collector.csv')
        content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(content))
        return df
    except client_s3.exceptions.NoSuchKey:
        print("Specified key does not exist")
        return pd.DataFrame(columns=['Timestamp', 'Price'])
    except Exception as ex:
        print(f"An error ocurred: {ex}" )
        return pd.DataFrame(columns=['Timestamp', 'Price'])

def upload_CVI_updated_dataset(dataframe: pd.DataFrame):
    csv_buffer = StringIO()
    dataframe.to_csv(csv_buffer, index=False)
    
    # Update the region to a valid one
    client_s3 = boto3.client('s3', region_name='us-east-1')  
    client_s3.put_object(Bucket='paus-bucket', Key='datasets/CVI_data_collector.csv', Body=csv_buffer.getvalue())

def main_job():
    """Main job for CVI Collector"""
    # Get last df version
    df_lastest = get_CVI_dataset()

    # Get new values
    today = datetime.now()
    df = get_volatility_index()

    # Add these values to the dataframe
    df_lastest = df_lastest._append({'Timestamp': today, 'Price': df}, ignore_index=True)
    
    # Update datafram from AWS
    upload_CVI_updated_dataset(df_lastest)

def get_cvi_historical_data(api_key):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    all_data = []

    while start_date > datetime(2020, 1, 1):  # Assuming CVI data starts from 2020
        url = 'https://t3index.p.rapidapi.com/historical'
        params = {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'symbol': 'CVI'
        }
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': 't3index.p.rapidapi.com'
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if 'data' in data:
            all_data.extend(data['data'])
        else:
            print(f"No data for the range {start_date} to {end_date}. Response: {data}")

        end_date = start_date
        start_date -= timedelta(days=365)

    return all_data

if __name__ == "__main__":
    # main_job()
    print(get_CVI_dataset())
    # api_key = 'e2d9224fa9msh6c8c343670a1f98p191281jsn8914f4ac48ad'
    # cvi_data = get_cvi_historical_data(api_key)
    # print(cvi_data)
