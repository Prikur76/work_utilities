#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import os.path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def _get_service_creds():
    """
        Проходим аутентификацию и возвращаем объект BUILD
        https://developers.google.com/sheets/api/quickstart/python
    """
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = None
    current_directory = os.path.dirname(os.path.realpath(__file__))
    creds_file = os.path.join(current_directory, "creds.json")
    creds = service_account.Credentials. \
        from_service_account_file(creds_file, scopes=scopes)
    build_connection = build('sheets', 'v4',
                             credentials=creds,
                             static_discovery=False)
    if not build_connection:
        raise HttpError
    return build_connection


def create_sheet(title, sheets=['']):
    """
    https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets
    Создание таблицы и листа/листов.
    Для создания по умолчанию параметр sheets = ['']
    Формат sheets:
        'sheets': [
            {'properties':
                {'title': title,
                'sheetType': 'GRID',
                'gridProperties':
                    {
                        'rowCount': 10,
                        'columnCount': 10,
                        'frozenRowCount': 1,
                        'frozenColumnCount': 0,
                        'hideGridlines': False,
                        'rowGroupControlAfter': False,
                        'columnGroupControlAfter': False
                    }
                }
            },
            # Additional sheets ....]
    пример:    NEW_SPREADSHEET_ID = create_sheet("NEW_TEST_SHEET", sheets)
    """
    service = _get_service_creds()
    sheet = service.spreadsheets()
    body = {
        'properties': {
            'title': title
        },
        'sheets': sheets
    }
    spreadsheet = sheet.create(body=body, fields='spreadsheetId').execute()
    print(f"     Spreadsheet ID: {(spreadsheet.get('spreadsheetId'))}")
    if spreadsheet:
        return spreadsheet.get('spreadsheetId')
    raise HttpError


def get_values(spreadsheet_id, range_name):
    """
    Запрос на данные из одного диапазона
    """
    service = _get_service_creds()
    sheet = service.spreadsheets()
    result = sheet.values()\
        .get(spreadsheetId=spreadsheet_id, range=range_name)\
        .execute()
    if result:
        return result
    raise HttpError


def batch_get_values(spreadsheet_id, range_names=[]):
    """
    https://developers.google.com/sheets/api/quickstart/python#step_3_set_up_the_sample
    Пакетный запрос на данные из МАССИВА ДИАПАЗОНОВ
    range_names = ["Sheet1!A1:B", "Sheet2!A1:B", ...]
    """
    service = _get_service_creds()
    sheet = service.spreadsheets()
    value_render_option = "FORMATTED_VALUE"
    result = sheet.values()\
        .batchGet(spreadsheetId=spreadsheet_id,
                  valueRenderOption=value_render_option,
                  ranges=range_names).execute()
    if result:
        return result
    raise HttpError


def update_values(spreadsheet_id, range_name, value_input_option, values):
    """
    Обновление ячеек в одном диапазоне таблицы.
    Форматы:
    value_input_option: "RAW" или "USER_ENTERED"
    values = [[# Cell values ...], # Additional rows ...]
    Пример:
    update_values("1CM29gwKIzeXsAppeNwrc8lbYaVMmUclprLuLYuHog4k",
                  "A1:C2", "USER_ENTERED",
                  [
                      ['A', 'B'],
                      ['C', 'D']
                  ])
    Чтобы очистить данные, используйте пустую строку ("")
    """
    service = _get_service_creds()
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


def batch_update_values(spreadsheet_id, range, data):
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
    service = _get_service_creds()
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
    service = _get_service_creds()
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


def append_values(spreadsheet_id, range_name, value_input_option, values):
    """
    Добавляет данные к ближайшим свободным ячейкам в ОДНОМ диапазоне
    Формат values:
        [[# Cell values ...], # Additional rows ...]
    Пример:
        append_values("1CM29gwKIzeXsAppeNwrc8lbYaVMmUclprLuLYuHog4k",
                      "A1:C2", "USER_ENTERED",
                      [
                          ['F', 'B'],
                          ['C', 'D']
                      ])
    """
    service = _get_service_creds()
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


def sheets_batch_update(spreadsheet_id, title, find, replacement):
    """
    https://developers.google.com/sheets/api/guides/batchupdate
    Обновляет заголовок электронной таблицы с помощью переменной title.
    Находит и заменяет значения ячеек в электронной таблице,
    используя переменные поиска и замены.
    Формируем пакет задач
    1. Изменение наименования таблицы.
    2. Найти и заменить текст
    + ... Добавление дополнительных запросов или операций
    через requests.append()...
    """
    service = _get_service_creds()
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
    if response:
        return response
    raise HttpError
