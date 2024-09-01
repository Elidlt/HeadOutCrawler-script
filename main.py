import logging
import sys

# Create a logger object
import requests
from bs4 import BeautifulSoup
import json
import sqlite3
import pandas as pd
import time, os
from dotenv import load_dotenv

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def setup_stdout_logger():
    # Create a logger object for stdout
    stdout_logger = logging.getLogger('stdout_logger')
    stdout_logger.setLevel(logging.INFO)  # Set the logging level for stdout

    # Create a stream handler for stdout
    stdout_handler = logging.StreamHandler()

    # Create a formatter and set it to the stdout handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    stdout_handler.setFormatter(formatter)

    # Add the stdout handler to the stdout logger
    stdout_logger.addHandler(stdout_handler)

    return stdout_logger


def setup_error_logger(log_file):
    # Create a logger object for error logging
    error_logger = logging.getLogger('error_logger')
    error_logger.setLevel(logging.ERROR)  # Set the logging level for errors

    # Create a file handler for logging errors to a file
    file_handler = logging.FileHandler(log_file)

    # Create a formatter and set it to the file handler
    formatter = logging.Formatter('%(asctime)s  - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the file handler to the error logger
    error_logger.addHandler(file_handler)

    return error_logger


# Set up the loggers
stdout_logger = setup_stdout_logger()
error_logger = setup_error_logger('error.log')

retry_strategy = Retry(
    total=20,  # Total number of retries
    backoff_factor=2,  # A delay between retries (e.g., 1 second, 2 seconds, 4 seconds)
    status_forcelist=[500, 502, 503, 504, 443],  # Retry for these HTTP status codes
)
adapter = HTTPAdapter(max_retries=retry_strategy)


def get_productsList():
    global json_data_2
    url2 = "https://www.headout.com/things-to-do-city-dubai/"
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.cookies.set('currentCurrency', 'AED')
    response2 = session.get(url2)
    soup2 = BeautifulSoup(response2.text, "html.parser")
    script_tag2 = soup2.find('script', id='__NEXT_DATA__')
    if script_tag2:
        json_data_2 = json.loads(script_tag2.string)
    else:
        print('Script tag not found.')
    d = json_data_2['props']['initialState']['productStore']['byCardId']

    return {Id: d[Id] for Id in d.keys()}


def get_productItems(pId, ParentElement):
    newUrl = f"https://www.headout.com/book/{pId}/select/?date="
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.cookies.set('currentCurrency', 'AED')
    response2 = session.get(newUrl)
    soup2 = BeautifulSoup(response2.text, "html.parser")
    script_tag2 = soup2.find('script', id='__NEXT_DATA__')
    if script_tag2:
        json_data_2 = json.loads(script_tag2.string)
    else:
        print('Script tag not found.')
    imageUrl = ParentElement['media']['productImages'][0]
    category = json_data_2['props']['initialState']['productStore']['byId'][pId]['primaryCategory'][
        'displayName']
    combo = ParentElement['combo']
    if combo:
        primaryCollection = ParentElement['name']
    else:
        primaryCollection = json_data_2['props']['initialState']['productStore']['byId'][pId]['primaryCollection'][
            'displayName']
    tourData = json_data_2['props']['initialState']['pricingStore']['byProductId'][f'{pId}']['inventoryMap']
    tourNames = {t['id']: t['parentProductName'] for t in
                 json_data_2['props']['initialState']['pricingStore']['byProductId'][f'{pId}']['tours']}
    tourInfo = {t['id']: t['variantInfo'] for t in
                json_data_2['props']['initialState']['pricingStore']['byProductId'][f'{pId}']['tours']}
    toursData = []
    for day in tourData:
        tours = tourData[day]
        for tId in tours:
            priceList = tours[tId][0]['priceProfile']['persons']
            prices = {priceList[i]['type']: priceList[i]['listingPrice'] for i in range(len(priceList))}
            toursData.append({
                "baseId": pId,
                "tourId": int(tId), "category": category,
                "MainCollection": primaryCollection,
                "name": tourNames[int(tId)],
                "info": tourInfo[int(tId)],
                "date": day,
                "start": tours[tId][0]['startTime'], "end": tours[tId][0]['endTime'],
                "price": prices, "currency": 'AED', "img": imageUrl['url'],
                "combo": combo})
    return toursData


def insert_data(data_list, run_time):
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    rows = []
    for data in data_list:
        rows.append((
            data['baseId'],
            data['tourId'],
            data['category'],
            data['MainCollection'],
            data['name'],
            data['info'],
            data['date'],
            data['start'],
            data['end'],
            json.dumps(data['price']),
            data['currency'],
            data['img'],
            data['combo'],
            run_time,
        ))
    cursor.executemany('''
        INSERT OR REPLACE INTO tours (base_tour_id,tour_id,category,
        main_collection, name, info, date, start_time, end_time, price,
         currency,img_url,combo, last_update)
        VALUES (?,?, ?, ?, ?, ?, ?, ?, ? , ? , ? , ?, ?, ?)
    ''', rows)

    # Commit the transaction
    conn.commit()
    conn.close()


def main():
    products = get_productsList()
    df_data = []
    cnt = 0
    for pId in products:

        if 5 > cnt:
            cnt += 1
            df_data.append(get_productItems(pId, products[pId]))
        else:
            cnt += 1

    flattened_list = [item for sublist in df_data for item in sublist]
    # Step 2: Convert to DataFrame
    df = pd.DataFrame(flattened_list)

    # Step 3: Save to CSV
    insert_data(flattened_list, round(time.time()))


def initDB():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
                CREATE TABLE IF NOT EXISTS tours (
                    base_tour_id INTEGER,
                    tour_id INTEGER,
                    category TEXT,
                    main_collection TEXT,
                    name TEXT,
                    info TEXT,
                    date TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    price REAL,
                    currency TEXT,
                    img_url TEXT,
                    combo BOOL,
                    last_update INTEGER,
                    PRIMARY KEY (tour_id, last_update)
                )
            ''')
    conn.commit()
    conn.close()


# Insert the data
if __name__ == '__main__':
    load_dotenv()
    debug = os.getenv('DEBUG')
    cycle = os.getenv("CYCLE")
    if bool(debug):
        stdout_logger.setLevel(logging.DEBUG)
    if not os.path.exists("db.sqlite"):
        stdout_logger.debug("Initialize Database for the first time...")
        initDB()

    while True:
        try:
            timestamp = round(time.time())
            stdout_logger.info(f"Run New Cycle in {timestamp}...")
            main()
        except Exception as e:
            stdout_logger.info("An error Happened")
            print(e)
            error_logger.error("an error happened..." , exc_info=True)

        time.sleep(int(cycle))
