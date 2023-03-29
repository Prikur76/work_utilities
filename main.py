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
                'Model', 'Number', 'VIN', 'Gas', 'Region', 'Department',
                'Status', 'SubStatus', 'Reason', 'Comment'
            ]
        ].values.tolist()

        for park in taxoparks.values():
            park_id, api_key, sheets_ids = park.values()
            roster = create_roster_for_report(
                park_id, api_key, active_drivers
            )
            drivers_records = roster.values.tolist()

            for sheet_id in sheets_ids:
                ss.batch_clear_values(
                    sheet_id, ranges=[range_for_update, cars_ranges_for_update]
                )
                ss.batch_update_values(
                    sheet_id, range_for_update, drivers_records
                )
                ss.batch_update_values(
                    sheet_id, cars_ranges_for_update, active_cars
                )

    except HttpError as ggl_http_err:
        logger.error('Ошибка подключения гугла: ', ggl_http_err)
    except requests.exceptions.HTTPError as http_err:
        logger.error('Ошибка запроса: ', http_err)
    except requests.exceptions.ConnectionError as connection_err:
        logger.error('Lost HTTP connection: ', connection_err)
        time.sleep(60)


if __name__ == '__main__':
    schedule.every().hour.at('29:00').do(main)
    schedule.every().hour.at('59:00').do(main)
    while True:
        schedule.run_pending()
        time.sleep(1)
