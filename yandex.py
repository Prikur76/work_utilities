import pandas as pd
import requests


class Taximeter:
    def __init__(self, park_id=None, api_key=None):
        self.park_id = park_id
        self.client_id = f'taxi/park/{park_id}'
        self.api_key = api_key

    def __str__(self):
        return "Park_ID:    %s\nClient_ID:  %s\nAPI-key:    %s" \
            % (self.park_id, self.client_id, self.api_key)

    def fetch_drivers_profiles(self):
        """Возвращает профили водителей. Метод POST"""
        url = 'https://fleet-api.taxi.yandex.net/v1/' \
              'parks/driver-profiles/list'
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
        with requests.post(url=url, json=payload,
                           headers=headers, stream=True) as response:
            response.raise_for_status()
            if response:
                roster = response.json()
                drivers_profiles = roster['driver_profiles']
                total = roster['total']
                if total > 1000:
                    offsets = [i for i in range(1, total, 1000)]
                    for offset in offsets:
                        payload['offset'] = offset
                        payload['limit'] = 1000
                        with requests.post(
                                url=url,
                                json=payload,
                                headers=headers,
                                stream=True) as offset_response:
                            offset_response.raise_for_status()
                            driver_profiles = \
                                offset_response.json()['driver_profiles']
                            drivers_profiles.extend(driver_profiles)
                return drivers_profiles
            raise requests.exceptions.HTTPError('Request failed')

    def fetch_active_balances(self):
        """Возвращает список активных водителей."""
        drivers_profiles = self.fetch_drivers_profiles()
        working_drivers = [
            x for x in drivers_profiles
            if (x['driver_profile']['work_status'] == 'working') | ('car' in x.keys())
        ]
        roster = [
            {
                'ya_id': driver['driver_profile']['id'],
                'ya_balance': driver['accounts'][0]['balance'],
            } for driver in working_drivers
        ]
        balances = pd.DataFrame(roster)
        balances['ya_balance'] = pd.to_numeric(
            balances['ya_balance'], downcast='integer'
        )
        return balances

    def fetch_cars(self):
        """Возвращает 'сырой' список машин. Метод POST"""
        url = 'https://fleet-api.taxi.yandex.net/' \
              'v1/parks/cars/list'
        headers = {
            'X-Client-ID': self.client_id,
            'X-API-Key': self.api_key,
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
        with requests.post(url=url, json=payload,
                           headers=headers, stream=True) as response:
            response.raise_for_status()
            if response:
                roster = response.json()
                cars = roster['cars']
                total = roster['total']
                if total > 1000:
                    offsets = [i for i in range(1, total, 1000)]
                    for offset in offsets:
                        payload['offset'] = offset
                        payload['limit'] = 1000
                        with requests.post(
                                url=url,
                                json=payload,
                                headers=headers,
                                stream=True) as offset_response:
                            offset_response.raise_for_status()
                            cars_fragment = offset_response.json()['cars']
                            cars.extend(cars_fragment)
                return cars
            raise requests.exceptions.HTTPError('Request failed')

    def fetch_workrules(self):
        """Возвращает список условий работы. Метод GET"""
        url = 'https://fleet-api.taxi.yandex.net/' \
              'v1/parks/driver-work-rules'
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
        if response:
            return response.json()
        raise requests.exceptions.HTTPError('Request failed')

    def fetch_transaction_categories(self):
        """Возвращает список категорий транзакций. Метод POST"""
        url = 'https://fleet-api.taxi.yandex.net/' \
              'v2/parks/transactions/categories/list'
        headers = {
            'X-Client-ID': self.client_id,
            'X-API-Key': self.api_key,
            'Accept-Language': 'ru'
        }
        payload = {
            'query': {
                'category': {
                    'is_affecting_driver_balance': True,
                    'is_creatable': False,
                    'is_editable': False,
                    'is_enabled': True,
                },
                'park': {
                    'id': self.park_id
                }
            }
        }
        response = requests.post(url=url, json=payload, headers=headers)
        response.raise_for_status()
        if response:
            return response.json()['categories']
        raise requests.exceptions.HTTPError('Request failed')

    def fetch_vehicle_profile(self, vehicle_id):
        """
        !!!НЕ РАБОТАЕТ, NEED TEST!!!
        Возвращает информацию об автомобиле.
        Метод GET
        """
        url = 'https://fleet-api.taxi.yandex.net/v2/parks/vehicles/car'
        headers = {
            'X-Park-ID': self.park_id,
            'X-Client-ID': self.client_id,
            'X-API-Key': self.api_key
        }
        params = {
            'vehicle_id': vehicle_id
        }
        response = requests.get(url=url, params=params, headers=headers)
        response.raise_for_status()
        if response:
            return response.json()
        raise requests.exceptions.HTTPError('Request failed')

    def fetch_contractor_profile(self, contractor_profile_id):
        """
        !!!НЕ РАБОТАЕТ, NEED TEST!!!
        Возвращает профиль водителя/курьера.
        Метод GET
        """
        url = 'https://fleet-api.taxi.yandex.net/' \
              'v2/parks/contractors/driver-profile'
        headers = {
            'X-Park-ID': self.park_id,
            'X-Client-ID': self.client_id,
            'X-API-Key': self.api_key
        }
        params = {
            'contractor_profile_id': contractor_profile_id
        }
        response = requests.get(url=url, params=params, headers=headers)
        response.raise_for_status()
        if response:
            return response.json()
        raise requests.exceptions.HTTPError('Request failed')
