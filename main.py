#!/usr/bin/python

import logging
import os
import time

import requests
import schedule
from dotenv import load_dotenv
from googleapiclient.errors import HttpError

import element as el
import spreadsheets as ss
import yandex as ya

logger = logging.getLogger(__name__)


def create_roster_for_report(park_id, api_key, active_drivers):
    """Обновляем таблицу с отчетом в гугле"""
    park = ya.Taximeter(park_id, api_key)
    active_balances = park.fetch_active_balances()
    roster = active_balances\
        .merge(active_drivers, how='left',
               left_on='ya_id', right_on='DefaultID') \
        .drop(columns=['ya_id', 'DefaultID']) \
        .dropna(subset=['FIO'])
    sorted_balances = roster[
        ['FIO', 'PhoneNumber', 'DatePL', 'ya_balance',
         'ConsolidBalance', 'Car', 'NameConditionWork']
    ]\
        .sort_values(by=['Car', 'DatePL'],
                     ascending=[True, False])\
        .drop_duplicates()
    return sorted_balances


def main():
    logging.basicConfig(
        format='[%(levelname)s] - %(asctime)s - %(name)s - %(message)s',
        level=logging.INFO
    )

    load_dotenv()
    user = os.environ.get('ELEMENT_LOGIN')
    password = os.environ.get('ELEMENT_PASSWORD')
    drivers_url = os.environ.get('ELEMENT_DRIVERS_URL')
    cars_url = os.environ.get('ELEMENT_CARS_URL')
    taxoparks = {
        'reports': {
            'park_id': None,
            'api_key': None,
            'sheets_ids': [os.environ.get('REPORT_SPREADSHEET_ID')],
            'region': None,
        },
        'moscow': {
            'park_id': os.environ.get('MSK_PARK_ID'),
            'api_key': os.environ.get('MSK_X_API_KEY'),
            'sheets_ids': [os.environ.get('MSK_SPREADSHEET_ID')],
            'region': os.environ.get('MSK_REGION'),
        },
        'ekaterinburg': {
            'park_id': os.environ.get('EKB_PARK_ID'),
            'api_key': os.environ.get('EKB_X_API_KEY'),
            'sheets_ids': [os.environ.get('EKB_SPREADSHEET_ID')],
            'region': os.environ.get('EKB_REGION')
        },
        'yaroslavl': {
            'park_id': os.environ.get('YAR_PARK_ID'),
            'api_key': os.environ.get('YAR_X_API_KEY'),
            'sheets_ids': [
                os.environ.get('YAR_SPREADSHEET_ID'),
                os.environ.get('KSTR_SPREADSHEET_ID')
            ],
            'region': os.environ.get('YAR_REGION')
        },
        'kirov': {
            'park_id': os.environ.get('KRV_PARK_ID'),
            'api_key': os.environ.get('KRV_X_API_KEY'),
            'sheets_ids': [os.environ.get('KRV_SPREADSHEET_ID')],
            'region': os.environ.get('KRV_REGION')
        }
    }
    range_for_update = os.environ.get('RANGE_FOR_UPDATE')
    cars_ranges_for_update = os.environ.get('RANGE_CARS_FOR_UPDATE')

    try:
        element = el.Element(user, password)
        exclude_roster = [
            '', 'Комфорт', 'Подключашки 2 %', 'ПОДКЛЮЧАШКА 3%', 'Штатный'
        ]
        active_drivers = element.fetch_active_drivers(
            url=drivers_url, conditions_exclude=exclude_roster
        )
        cars = element.fetch_active_cars(cars_url)
        active_cars = cars[
            [
                'Model', 'Number', 'VIN', 'YearCar', 'MileAge',
                'Region', 'Status', 'SubStatus', 'Reason',
                'Comment',
            ]
        ]

        for park in taxoparks.values():
            park_id, api_key, sheets_ids, region = park.values()
            if park_id and api_key and region:
                roster = create_roster_for_report(
                    park_id, api_key, active_drivers
                )
                drivers_records = roster.values.tolist()
                region_filter = (active_cars.Region == region)
                cars_for_upload = active_cars[region_filter].values.tolist()
                for sheet_id in sheets_ids:
                    ss.batch_clear_values(
                        sheet_id,
                        ranges=[range_for_update, cars_ranges_for_update]
                    )
                    ss.batch_update_values(
                        sheet_id, range_for_update, drivers_records
                    )
                    ss.batch_update_values(
                        sheet_id, cars_ranges_for_update, cars_for_upload
                    )
            else:
                cars_for_upload = active_cars.values.tolist()
                for sheet_id in sheets_ids:
                    ss.batch_clear_values(
                        sheet_id, ranges=[cars_ranges_for_update]
                    )
                    ss.batch_update_values(
                        sheet_id, cars_ranges_for_update, cars_for_upload
                    )

    except HttpError as ggl_http_err:
        logger.error(
            msg=f'Ошибка подключения гугла: {ggl_http_err}',
            stack_info=False
        )
    except requests.exceptions.HTTPError as http_err:
        logger.error(
            msg=f'Ошибка запроса: {http_err}',
            stack_info=False
        )
    except requests.exceptions.ChunkedEncodingError as chunked_err:
        logger.error(
            msg=f'Ошибка обработки пакета: {chunked_err}',
            stack_info=False
        )
    except requests.exceptions.ConnectionError as connection_err:
        logger.error(
            msg=f'Lost HTTP connection: {connection_err}',
            stack_info=False
        )
        time.sleep(60)
    except requests.exceptions.Timeout as timeout_err:
        logger.error(
            msg=f'Timeout: {timeout_err}',
            stack_info=False
        )
        time.sleep(300)


if __name__ == '__main__':
    while True:
        main()
        time.sleep(900)
    # schedule.every().hour.at('14:00').do(main)
    # schedule.every().hour.at('29:00').do(main)
    # schedule.every().hour.at('44:00').do(main)
    # schedule.every().hour.at('59:00').do(main)
    # while True:
        # schedule.run_pending()
        # time.sleep(1)
