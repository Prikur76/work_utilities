#!/usr/bin/python
import logging
import time

import requests
from environs import Env
from googleapiclient.errors import HttpError

import element as el
import settings as st
import spreadsheets as ss
import yandex as ya

env = Env()
env.read_env()

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

def update_google_sheet(active_cars, active_drivers, park):
    """
    Обновляет таблицу с отчетом в гугле
    """
    sheets_ids = park['sheets_ids']
    park_cars = active_cars[
        active_cars['Region'] == park['region']
    ].values.tolist()

    park_drivers = []
    for i in park['yandex']:
        park_drivers += create_roster_for_report(
            i['park_id'], i['api_key'], active_drivers
        ).values.tolist()

    for sheet_id in sheets_ids:
        ss.batch_clear_values(sheet_id,
                              ranges=[st.DRIVERS_RANGE_FOR_UPDATE])
        ss.batch_update_values(sheet_id,
                               st.DRIVERS_RANGE_FOR_UPDATE,
                               park_drivers)
        ss.batch_update_values(sheet_id,
                               st.CARS_RANGE_FOR_UPDATE,
                               park_cars)


def main():
    logging.basicConfig(
        format='[%(levelname)s] - %(asctime)s - %(name)s - %(message)s',
        level=logging.INFO
    )

    element = el.Element(st.USER, st.PASSWORD)
    reports_sheets_ids = st.REPORTS_SHEETS_IDS

    try:
        active_drivers = element.fetch_active_drivers(
            url=st.DRIVERS_URL,
            conditions_exclude=st.EXCLUDE_ROSTER)
        element_cars = element.fetch_active_cars(st.CARS_URL)
        active_element_cars = element_cars[
            [
                'Model', 'Number', 'VIN', 'YearCar', 'MileAge',
                'Region', 'Status', 'SubStatus', 'Reason',
                'Comment',
            ]
        ]
        all_active_cars = active_element_cars.values.tolist()

        for sheet_id in reports_sheets_ids:

            ss.batch_clear_values(sheet_id,
                                  ranges=[st.CARS_RANGE_FOR_UPDATE])

            ss.batch_update_values(sheet_id,
                                   st.CARS_RANGE_FOR_UPDATE,
                                   all_active_cars)

        update_google_sheet(active_element_cars,
                            active_drivers, st.MSK_PARKS)
        update_google_sheet(active_element_cars,
                            active_drivers, st.EKAT_PARKS)
        update_google_sheet(active_element_cars,
                            active_drivers, st.YAR_PARKS)

    except HttpError as ggl_http_err:
        logger.error(msg=f'Ошибка подключения гугла: {ggl_http_err}',
                     stack_info=False)
    except requests.exceptions.HTTPError as http_err:
        logger.error(msg=f'Ошибка http-запроса: {http_err}',
                     stack_info=False)
    except requests.exceptions.ChunkedEncodingError as chunked_err:
        logger.error(msg=f'Ошибка обработки пакета: {chunked_err}',
                     stack_info=False)
    except requests.exceptions.Timeout as timeout_err:
        logger.error(msg=f'Timeout: {timeout_err}',
                     stack_info=False)
        time.sleep(300)
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(msg=f'Ошибка HTTP соединения: {conn_err}',
                     stack_info=False)
        time.sleep(60)


if __name__ == '__main__':
    while True:
        main()
        time.sleep(900)
