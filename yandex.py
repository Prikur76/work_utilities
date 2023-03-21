# -*- coding: utf-8 -*-
import requests


class Taximeter:
    """Класс Таксометр"""
    def __init__(self, park_id=None, api_key=None):
        self.park_id = park_id
        self.client_id = f'taxi/park/{park_id}'
        self.api_key = api_key
        print('Create instance of Yandex Taximeter')

    def __str__(self):
        return "Park_ID:    %s\nClient_ID:  %s\nAPI-key:    %s" \
               % (self.park_id, self.client_id, self.api_key)

    def fetch_drivers_profiles(self):
        """Возвращает профили водителей. Метод POST"""
        url = 'https://fleet-api.taxi.yandex.net/v1/parks/driver-profiles/list'
        headers = {
            'X-Client-ID': self.client_id,
            'X-API-Key': self.api_key,
            'Accept-Language': 'ru'
        }
        payload = {
            'fields': {
                'account': ['balance', 'last_transaction_date'],
                'car': ['vin', 'number'],
                'current_status': ['status', 'status_updated_at'],
                'driver_profile': [
                    'id', 'first_name', 'middle_name', 'last_name',
                    'phones', 'driver_license', 'created_date',
                    'work_rule_id', 'work_status', 'check_message',
                    'comment'
                ],
                'park': ['name'],
            },
            'limit': 1000,
            'offset': 0,
            'query': {
                'park': {
                    'id': self.park_id
                },
                'text': ''
            },
            'sort_order': [
                {
                    'direction': 'desc',
                    'field': 'driver_profile.created_date'
                }
            ]
        }
        response = requests.post(url=url, json=payload, headers=headers)
        response.raise_for_status()
        roster = response.json()
        drivers_profiles = roster['driver_profiles']
        print(f'Start: ', drivers_profiles[-1])
        total = roster['total']
        if total > 1000:
            offsets = [i for i in range(1, total, 1000)]
            for offset in offsets:
                payload['offset'] = offset
                payload['limit'] = 1000
                response = requests.post(url=url, json=payload,
                                         headers=headers)
                response.raise_for_status()
                driver_profiles = response.json()['driver_profiles']
                print(f'Last_{offset}: ', driver_profiles[-1])
                drivers_profiles.extend(driver_profiles)
        return drivers_profiles

    def fetch_cars(self):
        """Возвращает 'сырой' список машин. Метод POST"""
        url = 'https://fleet-api.taxi.yandex.net/v1/parks/cars/list'
        headers = {
            'X-Client-ID': self.client_id,
            'X-API-Key': self.api_key,
            'Accept-Language': 'ru'
        }
        payload = {
            'limit': 1000,
            'offset': 0,
            'query': {
                'park': {
                    'id': self.park_id
                },
                'text': ''
            }
        }
        response = requests.post(url=url, json=payload, headers=headers)
        response.raise_for_status()
        roster = response.json()
        cars = roster['cars']
        total = roster['total']
        if total > 1000:
            offsets = [i for i in range(1, total, 1000)]
            for offset in offsets:
                payload['offset'] = offset
                payload['limit'] = 1000
                response = requests.post(url=url, json=payload,
                                         headers=headers)
                response.raise_for_status()
                cars_fragment = response.json()['cars']
                cars.extend(cars_fragment)
        return cars

    def fetch_workrules(self):
        """Получение списка условий работы. Метод GET"""
        url = 'https://fleet-api.taxi.yandex.net/v1/parks/driver-work-rules'
        headers = {
            'X-Client-ID': self.client_id,
            'X-API-Key': self.api_key,
            'Accept-Language': 'ru'
        }
        payload = {
            'park_id': self.park_id
        }
        response = requests.get(url=url, params=payload, headers=headers)
        response.raise_for_status()
        workrules = response.json()
        return workrules

    def fetch_transaction_categories(self):
        """Возвращает список категорий транзакций. Метод POST"""
        url = 'https://fleet-api.taxi.yandex.net/v2/parks/transactions/categories/list'
        headers = {
            'X-Client-ID': self.client_id,
            'X-API-Key': self.api_key,
            'Accept-Language': 'ru'
        }
        payload = {
            'query': {
                'category': {
                    'is_affecting_driver_balance': true,
                    'is_creatable': false,
                    'is_editable': false,
                    'is_enabled': true
                },
                'park': {
                    'id': self.park_id
                }
            }
        }
        response = requests.post(url=url, json=payload, headers=headers)
        response.raise_for_status()
        transaction_categories = response.json()['categories']
        return transaction_categories


    def get_profile_car(self, vehicle_id: str):
        """
        !!! Не работает !!!
        Получение профиля автомобиля. Метод GET
        :param vehicle_id:
        :return:
        """
        url = 'https://fleet-api.taxi.yandex.net/v2/parks/vehicles/car?vehicle_id=%s' % (vehicle_id)
        print(url)
        payload = '{"park": {"id": "%s"}}' % (self.park_id)
        response = requests.get(url=url,
                                params=payload,
                                headers=({"X-Park-ID":   self.park_id,
                                          "X-Client-ID": self.client_id,
                                          "X-API-Key":   self.api_key}))

        if response.status_code == 200:
            res = json.loads(response.text)
            return res
        else:
            return response.status_code

    def get_plofile_driver(self, driver_id):
        """
        !!! Не работает !!!
        Получение профиля водителя. Метод GET
        :param driver_id:
        :return:
        """
        url = 'https://fleet-api.taxi.yandex.net/v2/parks/contractors/driver-profile?contractor_profile_id=%s' % (driver_id)
        print(url)
        payload = '{"park": {"id": "%s"}}' % (self.park_id)
        response = requests.get(url=url,
                                params=payload,
                                headers=({"X-Park-ID":   self.park_id,
                                          "X-Client-ID": self.client_id,
                                          "X-API-Key":   self.api_key}))
        if response.status_code == 200:
            res = json.loads(response.text)
            return res
        else:
            return response.status_code