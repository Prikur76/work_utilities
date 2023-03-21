import os

import pandas as pd
import requests
from dotenv import load_dotenv

import tools

load_dotenv()

pd.set_option('mode.chained_assignment', None)


def get_raw_drivers_roster():
    """Возвращает список водителей 1с в формате .json"""
    user = os.environ.get('LOGIN_1C')
    password = os.environ.get('PASSWORD_1C')
    url = 'https://taksi.0nalog.com:1703/Transavto/hs/Driver/v1/Get'
    response = requests.get(url=url, auth=(user, password))
    response.raise_for_status()
    return response.json()


def fetch_working_drivers():
    """Возвращает отфильтрованный список работающих водителей"""
    raw_drivers_roster = get_raw_drivers_roster()
    drivers = pd.DataFrame(raw_drivers_roster)
    filter = (drivers.Status == 'Работает') & \
             (drivers.ExternalCar == False) & \
             (~drivers.NameConditionWork.isin(
                 [
                    '', 'Комфорт', 'Подключашки 2 %',
                    'ПОДКЛЮЧАШКА 3%', 'Штатный'
                 ]
             )) & \
             (~drivers.PhoneNumber.isin([''])) & \
             (~drivers.DriversLicenseSerialNumber.isin([''])) & \
             (~drivers.Car.isin(['']))

    filtered_roster = drivers[filter]
    filtered_roster['Contract'] = None
    filtered_roster.loc[:, 'Contract'] = filtered_roster.apply(
        lambda x: tools.create_contract(
            tools.format_date_string(x['BeginContract']),
            tools.format_date_string(x['EndContract'])
        ), axis=1)
    filtered_roster.loc[:, 'DatePL'] = filtered_roster['DatePL']\
        .apply(tools.format_date_string, format='%Y-%m-%d')
    filtered_roster.loc[:, 'PhoneNumber'] = filtered_roster['PhoneNumber'] \
        .apply(tools.remove_chars)
    working_drivers = filtered_roster[
        [
            'FIO', 'PhoneNumber', 'Contract', 'Car', 'DatePL',
            'NameConditionWork', 'ConsolidBalance',
        ]
    ].sort_values(by=['DatePL'], ascending=[True])
    return working_drivers
