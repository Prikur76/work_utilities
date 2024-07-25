#!/usr/bin/python
import logging
import time
from datetime import datetime

import numpy as np
import pytz
import requests
from googleapiclient.errors import HttpError

import element as el
import settings as st
import spreadsheets as ss
import tools as tl

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        format='[%(levelname)s] - %(asctime)s - %(name)s - %(message)s',
        level=logging.INFO
    )
    element = el.Element(st.USER, st.PASSWORD)

    try:
        active_drivers = element.fetch_active_drivers(
            url=st.DRIVERS_URL, conditions_exclude=st.EXCLUDE_ROSTER)

        # Форматирование списка работающих водителей
        active_drivers = active_drivers\
            .sort_values(by=['CarDepartment', 'Car', 'DatePL'],
                         ascending=[True,True, True])
        active_drivers['Phones'] = active_drivers.apply(
            lambda row: tl.format_driver_phones(row), axis=1)
        active_drivers['PassportInfo']= active_drivers.apply(
            lambda row: tl.format_passport_info(row), axis=1)
        active_drivers['DriverLicenseInfo'] = active_drivers.apply(
            lambda row: tl.format_driver_license(row), axis=1)
        formatted_active_drivers = active_drivers[
            [
                'ID', 'FIO', 'Sex', 'BirthDate', 'Phones', 'PassportInfo',
                'PassportRegistrationAddress', 'ActualAddress',
                'DriverLicenseInfo', 'Comment', 'SNILS', 'INN',
                'DriverDateCreate', 'EmploymentDate', 'DismissalDate',
                'Experience', 'NameConditionWork', 'Car', 'CarDepartment',
                'BeginContract', 'EndContract', 'DatePL',
                'ConsolidBalance', 'Supervisor', 'KIS_ART_DriverId',
                'Marketing', 'DefaultID'
            ]
        ].sort_values(by=['FIO'], ascending=[True])
        formatted_active_drivers['DateUpload'] = datetime.now(pytz.timezone('Europe/Moscow'))\
            .strftime("%d.%m.%Y %H:%M:%S")

        # Записываем в гугл
        ss.batch_update_values(st.REPORT_ID, st.RANGE_FOR_UPLOAD_DRIVERS,
                               formatted_active_drivers.values.tolist())

        # Отбираем нужные данные
        drivers = active_drivers[
            ['FIO', 'PhoneNumber', 'Balance', 'DatePL', 'Car', 'NameConditionWork']
        ]
        drivers['DriverInfo'] = drivers.apply(
            lambda row: tl.format_driver_info(row), axis=1)
        sorted_drivers = drivers.sort_values(
            by=['Car', 'DatePL'], ascending=[True, True])

        driver_info_list = sorted_drivers[['Car', 'DriverInfo', 'DatePL']]\
            .groupby('Car')['DriverInfo']\
            .agg(list)\
            .reset_index(name='DriverInfo')

        driver_info_list['DriverInfo'] = driver_info_list.apply(
            lambda row: '\n\n'.join(list(set(row['DriverInfo'])))
            if len(list(set(row['DriverInfo']))) > 1
            else ''.join(list(set(row['DriverInfo']))),axis=1)

        # Извлекаем общий список автомобилей из 1с
        active_cars = element.fetch_active_cars(st.CARS_URL)

        active_cars['Transmission'] = np.select(
            [active_cars['KPPType'] == 'АКПП',
             active_cars['KPPType'] == 'МКПП', active_cars['KPPType'] == ''],
            ['АТ', 'МТ', ''], default='' )
        active_cars['GBO'] = np.select(
            [active_cars['Gas'] == True, active_cars['Gas'] == False],
            ['ГБО', ''], default='')
        active_cars['STSSeriesNumber'] = active_cars.apply(
            lambda row: ''.join([row['STSSeries'], row['STSNumber']]) if row['STSNumber'] else '',
            axis=1)
        active_cars['STSDetail'] = active_cars.apply(lambda row:  tl.format_sts_detail(row), axis=1)
        active_cars['OSAGOSeriesNumber'] = active_cars.apply(
            lambda row: ' '.join([row['OSAGOSeries'], row['OSAGONumber']]) if row['OSAGONumber'] else '',
            axis=1)
        active_cars['OSAGODetail'] = active_cars.apply(
            lambda row:  tl.format_osago_detail(row), axis=1)
        active_cars['TODetail'] = active_cars.apply(
            lambda row:  tl.format_dc_detail(row), axis=1)
        active_cars['LicenseDetail'] = active_cars.apply(
            lambda row:  tl.format_license_detail(row), axis=1)
        active_cars['CarInfo'] = active_cars.apply(
            lambda row: tl.format_car_info(row), axis=1)
        active_cars['StatusDetail'] = active_cars.apply(
            lambda row: tl.format_status_detail(row), axis=1)
        active_cars['FormattedCommentCar'] = active_cars.apply(
            lambda row: tl.format_comment_car(row), axis=1)
        active_cars['CarLocation'] = active_cars.apply(
            lambda row: tl.fetch_car_location(row), axis=1)
        active_cars['DateUpload'] = datetime.now(pytz.timezone('Europe/Moscow'))\
            .strftime("%d.%m.%Y %H:%M:%S")

        # Объединяем данные водителей и машин, сортируем и удаляем дубликаты
        merged_roster = active_cars.merge(
            driver_info_list, how='left', left_on='Number', right_on='Car')\
            .drop_duplicates(subset=['VIN'], keep='first')\
            .fillna('')\
            .sort_values(by=['Region', 'Department', 'Model', 'VIN'],
                         ascending=[True, True, True, True])

        roster_for_upload = merged_roster[
            [
                'CarInfo', 'Model', 'Number', 'VIN', 'YearCar', 'Transmission',
                'GBO', 'MileAge', 'BodyColor', 'Brand', 'LandLord', 'Organization',
                'STSDetail', 'STSSeriesNumber', 'STSIssueDate', 'STSValidityDate',
                'TODetail', 'TOSeriesNumber', 'TOIssueDate', 'TOValidityDate',
                'OSAGOInsurer', 'OSAGODetail','OSAGOSeriesNumber', 'OSAGOIssueDate',
                'OSAGOValidityDate','LicenseLicensee', 'LicenseDetail', 'LicenseSeriesNumber',
                'LicenseIssueDate', 'LicenseValidityDate', 'StatusDetail', 'Status',
                'SubStatus', 'Reason', 'Comment', 'FormattedCommentCar', 'CarLocation',
                'Department', 'Region', 'DriverInfo', 'DateUpload'
            ]
        ]

        ss.batch_update_values(st.REPORT_ID, st.RANGE_FOR_UPLOAD,
                               roster_for_upload.values.tolist())

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
        logger.error(msg=f'Timeout: {timeout_err}', stack_info=False)
        time.sleep(300)
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(msg=f'Ошибка HTTP соединения: {conn_err}',
                     stack_info=False)
        time.sleep(60)


if __name__ == '__main__':
    while True:
        main()
        time.sleep(300)
