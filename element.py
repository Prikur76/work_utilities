import pandas as pd
import requests

import tools

pd.set_option('mode.chained_assignment', None)


class Element():
    def __init__(self, user=None, password=None):
        self.user = user
        self.password = password

    def get_drivers(self, url):
        """Возвращает список водителей 1с:Элемент в формате .json"""
        auth = (self.user, self.password)
        response = requests.get(url=url, auth=auth)
        response.raise_for_status()
        return response.json()

    def fetch_active_drivers(self, url, conditions_exclude=['',]):
        """Возвращает отфильтрованный список работающих водителей"""
        drivers_roster = self.get_drivers(url)
        drivers = pd.DataFrame(drivers_roster)
        filters = (drivers.Status == 'Работает') & \
                 (drivers.ExternalCar == False) & \
                 (~drivers.NameConditionWork.isin(conditions_exclude)) & \
                 (~drivers.PhoneNumber.isin([''])) & \
                 (~drivers.DriversLicenseSerialNumber.isin([''])) & \
                 (~drivers.Car.isin(['']))
        filtered_roster = drivers[filters]
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
        active_drivers = filtered_roster[
            [
                'FIO', 'PhoneNumber', 'Contract', 'Car', 'DatePL',
                'NameConditionWork', 'ConsolidBalance',
            ]
        ].sort_values(by=['DatePL'], ascending=[True])
        return active_drivers

    def get_cars(self, url, inn=None):
        """Возвращает список всех машин из 1с:Элемент в формате .json. Метод GET"""
        params = {
            'inn': inn
        }
        auth = (self.user, self.password)
        response = requests.get(url=url, params=params, auth=auth)
        response.raise_for_status()
        return response.json()

    def fetch_activity_cars(self, url, inn=None):
        """Возвращает список активных машин из 1с:Элемент. Метод GET"""
        cars_roster = self.get_cars(url, inn)
        cars = pd.DataFrame(cars_roster)
        filters = (cars.Activity == True) & (~cars.Status.isin(['АРХИВ', ]))
        return cars[filters].sort_values(by='Code', ascending=True)

    def fetch_waybills(self, url, inn=None, phone=None,
                       start_date=None, end_date=None):
        """Возвращает список путевых листов"""
        auth = (self.user, self.password)
        payload = {
            'CompanyINN': inn,
            'PhoneNumber': phone,
            'Date1': start_date,
            'Date2': end_date
        }
        response = requests.post(url=url, json=payload, auth=auth)
        response.raise_for_status()
        return response.json()
