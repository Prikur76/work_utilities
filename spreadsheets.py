from __future__ import print_function

import os
import socket

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

socket.setdefaulttimeout(150)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
service_account_file = os.path.join(BASE_DIR, 'creds.json')


def create_build_connection():
    """
        Проходим аутентификацию и возвращаем объект BUILD
        https://developers.google.com/sheets/api/quickstart/python
    """
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = service_account.Credentials\
        .from_service_account_file(service_account_file, scopes=scopes)
    return build('sheets', 'v4', credentials=creds,
                 static_discovery=False, cache_discovery=False)


def get_values(spreadsheet_id, range_name):
    """
    Запрос на данные из одного диапазона
    """
    service = create_build_connection()
    sheet = service.spreadsheets()
    result = sheet.values()\
        .get(spreadsheetId=spreadsheet_id, range=range_name)\
        .execute()
    if result:
        return result
    raise HttpError


def batch_get_values(spreadsheet_id, range_names):
    """
    https://developers.google.com/sheets/api/quickstart/python#step_3_set_up_the_sample
    Пакетный запрос на данные из МАССИВА ДИАПАЗОНОВ
    range_names = ["Sheet1!A1:B", "Sheet2!A1:B", ...]
    """
    service = create_build_connection()
    sheet = service.spreadsheets()
    value_render_option = "FORMATTED_VALUE"
    result = sheet.values()\
        .batchGet(spreadsheetId=spreadsheet_id,
                  valueRenderOption=value_render_option,
                  ranges=range_names).execute()
    if result:
        return result
    raise HttpError


def batch_update_values(spreadsheet_id, sheet_range, data):
    """
    Обновление нескольких диапазонов таблицы
    Формат body:
         body = {
          'valueInputOption' : 'RAW',
          'data' : [
              {'range' : 'Лист2!D2', 'values' : get_values()},
              {'range' : 'Лист2!H4', 'values' : get_values()}
          ]
      }
    Формат data:
        [{'range': range_name, 'values': values},
        {'range': range_name2, 'values': values2}, ...]
    Форма values:
        [[# Cell values ...], # Additional rows ...]
    Пример:
        batch_update_values("1CM29gwKIzeXsAppeNwrc8lbYaVMmUclprLuLYuHog4k",
                            "A1:C2", "USER_ENTERED",
                            [
                                ['F', 'B'],
                                ['C', 'D']
                            ])
    """
    service = create_build_connection()
    batch_update_values_request_body = {
        "valueInputOption": "USER_ENTERED",
        "data": [
            {
                "range": sheet_range,
                "values": data
            }
        ]
    }
    sheet = service.spreadsheets()
    request = sheet.values()\
        .batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=batch_update_values_request_body
    )
    response = request.execute()
    if response:
        return response
    raise HttpError


def batch_clear_values(spreadsheet_id, ranges):
    """
    Очистка одного или нескольких диапазонов таблицы
    Формат body:
         body = {
          'ranges': []
      }
    Пример:
        batch_update_values("1CM29gwKIzeXsAppeNwrc8lbYaVMmUclprLuLYuHog4k",
                            ranges= ["Sheet1!A1:S", "Sheet2!A1:S"...])
    """
    service = create_build_connection()
    batch_clear_values_request_body = {
        "ranges": [
            ranges
        ]
    }
    sheet = service.spreadsheets()
    request = sheet.values()\
        .batchClear(
        spreadsheetId=spreadsheet_id,
        body=batch_clear_values_request_body
    )
    response = request.execute()
    if response:
        return response
    raise HttpError
