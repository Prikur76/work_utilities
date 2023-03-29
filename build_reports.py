import os
import pandas as pd
import numpy as np


from dotenv import load_dotenv

import element as el

load_dotenv()
xlsx_path = os.environ.get('XLSX_PATH')
user = os.environ.get('ELEMENT_LOGIN')
password = os.environ.get('ELEMENT_PASSWORD')

drivers_url = os.environ.get('ELEMENT_DRIVERS_URL')
cars_url = os.environ.get('ELEMENT_CARS_URL')

taxoparks = {
    'moscow': {
        'park_id': os.environ.get('MSK_PARK_ID'),
        'api_key': os.environ.get('MSK_X_API_KEY'),
        'sheets_ids': [os.environ.get('MSK_SPREADSHEET_ID')]
    },
    'ekaterinburg': {
        'park_id': os.environ.get('EKB_PARK_ID'),
        'api_key': os.environ.get('EKB_X_API_KEY'),
        'sheets_ids': [os.environ.get('EKB_SPREADSHEET_ID')]
    },
    'yaroslavl': {
        'park_id': os.environ.get('YAR_PARK_ID'),
        'api_key': os.environ.get('YAR_X_API_KEY'),
        'sheets_ids': [
            os.environ.get('YAR_SPREADSHEET_ID'),
            os.environ.get('KSTR_SPREADSHEET_ID')
        ]
    },
    'kirov': {
        'park_id': os.environ.get('KRV_PARK_ID'),
        'api_key': os.environ.get('KRV_X_API_KEY'),
        'sheets_ids': [os.environ.get('KRV_SPREADSHEET_ID')]
    }
}

catalog_id = os.environ.get('CATALOG_SS_ID')
car_ranges = os.environ.get('CATALOG_RANGES')
cars_ranges_for_update = os.environ.get('RANGE_CARS_FOR_UPDATE')

element = el.Element(user, password)
cars = element.fetch_active_cars(cars_url)
active_cars = cars[
    [
        'Model', 'Number', 'VIN', 'Gas', 'Region', 'Department',
        'Status', 'SubStatus', 'Reason', 'Comment'
    ]
]
msk_cars = active_cars[active_cars.Department.isin(['МОСКВА'],)]
# print(len(msk_cars))
# print(msk_cars)
# grouped_msk_cars = msk_cars.groupby(['Status', 'SubStatus']).agg({
#     'VIN': 'count',
# })
# print(grouped_msk_cars)
