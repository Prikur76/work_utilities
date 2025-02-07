import pandas as pd
import requests
import time


class Taximeter:
    def __init__(self, park_id=None, api_key=None):
        self.park_id = park_id
        self.client_id = f'taxi/park/{park_id}'
        self.api_key = api_key

    def __str__(self):
        return "Park_ID:    %s\nClient_ID:  %s\nAPI-key:    %s" \
            % (self.park_id, self.client_id, self.api_key)

    def fetch_drivers_profiles(self, updated_from: str = None, updated_to: str = None):
        """Возвращает профили водителей (курьеров).
        Формат даты (updated_from, updated_to): '2024-06-16T00:00:00Z'.
        Метод POST
        """
        url = 'https://fleet-api.taxi.yandex.net/v1/parks/driver-profiles/list'
        headers = {
            'X-Client-ID': self.client_id,
            'X-API-Key': self.api_key,
            'Accept-Language': 'ru'
        }
        payload = {
            'fields': {
                'account': [],
                'car': [],
                'park': [],
                'driver_profile': [
                    'id', 'first_name', 'middle_name', 'last_name',
                    'phones', 'driver_license', 'created_date',
                    'work_rule_id', 'work_status', 'check_message',
                    'comment', 'is_selfemployed', 'has_contract_issue',
                    'park_id'
                ],
                'current_status': ['status', 'status_updated_at']
            },
            'limit': 1000,
            'offset': 0,
            'query': {
                'park': {
                    'id': self.park_id,
                    'updated_at': {
                        'from': updated_from,
                        'to': updated_to
                    }
                },
                'text': ''
            },
            'sort_order': [
                {
                    'direction': 'asc',
                    'field': 'driver_profile.created_date'
                }
            ]
        }
        if updated_from is None and updated_to is None:
            del payload['query']['park']['updated_at']

        payload['offset'] = 0
        total = 1
        drivers_profiles = []
        while payload['offset'] <= total:
            with requests.post(url=url, headers=headers,
                               json=payload, stream=True) as response:
                response.raise_for_status()
                roster = response.json()
            drivers_profiles.extend(roster['driver_profiles'])
            total = roster['total']
            payload['offset'] += 1000
            time.sleep(1)
        return drivers_profiles

    def fetch_driver_profile_by_id(self, driver_id: str):
        """Возвращает профиль водителя по id. Метод GET"""
        url = f'https://fleet-api.taxi.yandex.net/v2/parks/contractors/driver-profile'
        headers = {
            'X-Park-ID': self.park_id,
            'X-Client-ID': self.client_id,
            'X-API-Key': self.api_key
        }
        payload = {
            'contractor_profile_id': driver_id
        }
        response = requests.get(url=url, headers=headers, params=payload)
        response.raise_for_status()
        return response.json()

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
                'ya_balance': float(driver['accounts'][0]['balance']) if 'accounts' in driver.keys() else 0.0,
            } for driver in working_drivers
        ]
        balances = pd.DataFrame(roster)
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
        return response.json()

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
        return response.json()['categories']
