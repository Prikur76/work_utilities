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
        with requests.get(url=url, auth=auth, stream=True) as response:
            response.raise_for_status()
            return response.json()

    def fetch_active_drivers(self, url, conditions_exclude=['', ]):
        """Возвращает отфильтрованный список работающих водителей"""
        drivers_roster = self.get_drivers(url)
        drivers = pd.DataFrame(drivers_roster)
        filters = (drivers.Status == 'Работает') & (~drivers.ExternalCar) & \
                  (~drivers.NameConditionWork.isin(conditions_exclude)) & \
                  (~drivers.PhoneNumber.isin([''])) & \
                  (~drivers.DriversLicenseSerialNumber.isin([''])) & \
                  (~drivers.Car.isin(['']))
        filtered_roster = drivers[filters]
        filtered_roster.loc[:, 'DatePL'] = filtered_roster['DatePL'] \
            .apply(tools.format_date_string, format='%Y-%m-%d')
        filtered_roster.loc[:, 'PhoneNumber'] = \
            filtered_roster['PhoneNumber'].apply(tools.remove_chars)
        active_drivers = filtered_roster[
            [
                'DefaultID', 'FIO', 'PhoneNumber', 'DatePL',
                'ConsolidBalance', 'Car', 'NameConditionWork',
            ]
        ].sort_values(by=['DatePL'], ascending=[True])
        return active_drivers

    def get_cars(self, url, inn=None):
        """Возвращает 'необработанный' список машин из 1с:Элемент. Метод GET"""
        params = {
            'inn': inn
        }
        auth = (self.user, self.password)
        with requests.get(url=url, params=params,
                          auth=auth, stream=True) as response:
            response.raise_for_status()
            return response.json()

    def fetch_active_cars(self, url, inn=None):
        """Возвращает список активных машин. Метод GET"""
        cars_roster = self.get_cars(url, inn)
        cars = pd.DataFrame(cars_roster)
        filters = cars.Activity & \
            ~cars.DisableDocumentStatus & \
            ~cars.DisableContract & \
            ~cars.Department.isin(['ЛИЧНАЯ', ]) & \
            ~cars.Status.isin(['АРХИВ', ])
        filtered_cars = cars[filters].sort_values(by='Code', ascending=True)
        filtered_cars.loc[:, 'YearCar'] = filtered_cars['YearCar']\
            .apply(tools.format_date_string, format='%Y')
        return filtered_cars
