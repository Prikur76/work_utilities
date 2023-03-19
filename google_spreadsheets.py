#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# https://developers.google.com/identity/protocols/oauth2/service-account#python

from __future__ import print_function

import os

from google.oauth2 import service_account
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


load_dotenv()


service_account_file = {
    'type': 'service_account',
    'project_id': os.environ.get('PROJECT_ID'),
    'private_key_id': os.environ.get('PRIVATE_KEY_ID'),
    'private_key': os.environ.get('PRIVATE_KEY'),
    'client_email': os.environ.get('CLIENT_EMAIL'),
    'client_id': os.environ.get('CLIENT_ID'),
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'token_uri': 'https://oauth2.googleapis.com/token',
    'auth_provider_x509_cert_url':
        'https://www.googleapis.com/oauth2/v1/certs',
    'client_x509_cert_url': os.environ.get('CLIENT_X509_CERT_URL')
}


class Sheet:
    def __init__(self, service_account):
        self.service_account_file = service_account_file

    def get_build(self):
        """
        Проходим аутентификацию и возвращаем объект BUILD
        https://developers.google.com/sheets/api/quickstart/python
        """
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        creds = None
        creds = service_account.Credentials\
            .from_service_account_file(self.service_account_file,
                                       scopes=SCOPES)
        return build('sheets', 'v4', credentials=creds, static_discovery=False)

    def create_sheet(self, title, sheets=['']):
        """
        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets
        Создание таблицы и листа/листов из списка.
        :param title:
        :param sheets:
        :return:
        """
        service = self.get_build()
        sheet = service.spreadsheets()
        body = {
            'properties': {
                'title': title
            },
            'sheets': sheets
        }
        spreadsheet = sheet\
            .create(body=body, fields='spreadsheetId')\
            .execute()
        if spreadsheet.get('spreadsheetId'):
            return spreadsheet.get('spreadsheetId')
        raise HttpError

    def get_values(self, spreadsheet_id, range_name):
        """
        Возвращает данные одного диапазона
        :param spreadsheet_id:
        :param range_name:
        :return:
        """
        service = self.get_build()
        sheet = service.spreadsheets()
        result = sheet.values()\
            .get(spreadsheetId=spreadsheet_id, range=range_name)\
            .execute()
        if result:
            return result
        raise HttpError

    def batch_get_values(self, spreadsheet_id, range_names):
        """
        https://developers.google.com/sheets/api/quickstart/python#step_3_set_up_the_sample
        Возвращает пакет данных из МАССИВА ДИАПАЗОНОВ
        range_names = ["Sheet1!A1:B", "Sheet2!A1:B", ...]
        :param spreadsheet_id:
        :param range_names:
        :return:
        """
        service = self.get_build()
        sheet = service.spreadsheets()
        value_render_option = "FORMATTED_VALUE"
        result = sheet.values()\
            .batchGet(spreadsheetId=spreadsheet_id,
                      valueRenderOption=value_render_option,
                      ranges=range_names).execute()
        if result:
            return result
        raise HttpError

    def update_values(self, spreadsheet_id, range_name,
                      value_input_option, values):
        """
        Обновление ячеек в одном диапазоне таблицы.
        :param spreadsheet_id:
        :param range_name:
        :param value_input_option:
        :param values:
        :return:
        """
        service = self.get_build()
        body = {
            'values': values
        }
        sheet = service.spreadsheets()
        result = sheet.values()\
            .update(spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body)\
            .execute()
        if result:
            return result
        raise HttpError

    def batch_update_values(self, spreadsheet_id, range, data):
        """
        Обновление нескольких диапазонов таблицы
        :param spreadsheet_id:
        :param range:
        :param data:
        :return:
        Формат data:
        [{'range': range_name, 'values': values},
        {'range': range_name2, 'values': values2}, ...]
        Форма values:
        [[# Cell values ...], # Additional rows ...]
        """
        service = self.get_build()
        batch_update_values_request_body = {
            "valueInputOption": "USER_ENTERED",
            "data": [
                {
                    "range": range,
                    "values": data
                }
            ]
        }
        sheet = service.spreadsheets()
        request = sheet.values()\
            .batchUpdate(spreadsheetId=spreadsheet_id,
                         body=batch_update_values_request_body)
        response = request.execute()
        if response:
            return response
        raise HttpError

    def batch_clear_values(self, spreadsheet_id, ranges):
        """
        Очистка одного или нескольких диапазонов таблицы
        :param spreadsheet_id:
        :param ranges:
        :return:
        Пример:
        batch_update_values("1CM29gwKIzeXsAppeNwrc8lbYaVMmUclprLuLYuHog4k",
                            ranges= ["Sheet1!A1:S", "Sheet2!A1:S"...])
        """
        service = self.get_build()
        batch_clear_values_request_body = {
            "ranges": [
                ranges
            ]
        }
        sheet = service.spreadsheets()
        request = sheet.values()\
            .batchClear(spreadsheetId=spreadsheet_id,
                        body=batch_clear_values_request_body)
        response = request.execute()
        if response:
            return response
        raise HttpError

    def append_values(self, spreadsheet_id, range_name,
                      value_input_option, values):
        """
        Добавляет данные к ближайшим свободным ячейкам в ОДНОМ диапазоне
        :param spreadsheet_id:
        :param range_name:
        :param value_input_option:
        :param values:
        :return:
        Пример:
        append_values("1CM29gwKIzeXsAppeNwrc8lbYaVMmUclprLuLYuHog4k",
        "A1:C2", "USER_ENTERED", [['F', 'B'],['C', 'D']])
        """
        service = self.get_build()
        body = {
            'values': values
        }
        sheet = service.spreadsheets()
        result = sheet.values()\
            .append(spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body)\
            .execute()
        if result:
            return result
        raise HttpError

    def sheets_batch_update(self, spreadsheet_id, title, find, replacement):
        """
        https://developers.google.com/sheets/api/guides/batchupdate
        Обновляет заголовок электронной таблицы с помощью переменной title.
        Находит и заменяет значения ячеек в электронной таблице, используя
        переменные поиска и замены.
        Формируем пакет задач:
        1. Изменение наименования таблицы.
        2. Найти и заменить текст
        + ... Добавление дополнительных запросов или операций
        через requests.append()...
        :param spreadsheet_id:
        :param title:
        :param find:
        :param replacement:
        :return:
        """
        service = self.get_build()
        requests = [{
            'updateSpreadsheetProperties': {
                'properties': {
                    'title': title
                },
                'fields': 'title'
            }
        }, {
            'findReplace': {
                'find': find,
                'replacement': replacement,
                'allSheets': True
            }
        }]
        body = {
            'requests': requests
        }
        sheet = service.spreadsheets()
        response = sheet\
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)\
            .execute()
        find_replace_response = response.get('replies')[1]\
            .get('findReplace')
        if find_replace_response:
            return find_replace_response
        raise HttpError

    def pivot_tables_base(self, spreadsheet_id):
        """
        https://developers.google.com/sheets/api/samples/pivot-tables
        Создает сводную таблицу по двум взаимосвязанным листам
        :param spreadsheet_id:
        :return:
        """
        service = self.get_build()
        # Создаем 2 листа для сводной таблицы.
        body = {
            'requests': [{
                'addSheet': {}
            }, {
                'addSheet': {}
            }]
        }
        batch_update_response = service.spreadsheets() \
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

        # Получаем id листа- источника и id целевого листа
        source_sheet_id = batch_update_response.get('replies')[0] \
            .get('addSheet').get('properties').get('sheetId')
        target_sheet_id = batch_update_response.get('replies')[1] \
            .get('addSheet').get('properties').get('sheetId')

        # Формируем запрос на создание сводной таблицы
        requests = [{
            'updateCells': {
                'rows': {
                    'values': [
                        {
                            'pivotTable': {
                                'source': {
                                    'sheetId': source_sheet_id,
                                    'startRowIndex': 0,
                                    'startColumnIndex': 0,
                                    'endRowIndex': 20,
                                    'endColumnIndex': 7
                                },
                                'rows': [
                                    {
                                        'sourceColumnOffset': 1,
                                        'showTotals': True,
                                        'sortOrder': 'ASCENDING',
                                    },
                                ],
                                'columns': [
                                    {
                                        'sourceColumnOffset': 4,
                                        'sortOrder': 'ASCENDING',
                                        'showTotals': True,
                                    }
                                ],
                                'values': [
                                    {
                                        'summarizeFunction': 'COUNTA',
                                        'sourceColumnOffset': 4
                                    }
                                ],
                                'valueLayout': 'HORIZONTAL'
                            }
                        }
                    ]
                },
                'start': {
                    'sheetId': target_sheet_id,
                    'rowIndex': 0,
                    'columnIndex': 0
                },
                'fields': 'pivotTable'
            }
        }]
        # Формируем body для пакетного обновления
        body = {
            'requests': requests
        }
        sheet = service.spreadsheets()
        response = sheet\
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)\
            .execute()
        if response:
            return response
        raise HttpError

    def pivot_tables_universal(self, spreadsheet_id, requests):
        """
        https://developers.google.com/sheets/api/samples/pivot-tables
        Создаем сводную таблицу по подготовленному requests
        :param spreadsheet_id:
        :param requests:
        :return:
        """
        service = self.get_build()
        body = {
            'requests': requests
        }
        sheet = service.spreadsheets()
        response = sheet\
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)\
            .execute()
        if response:
            return response
        raise HttpError
