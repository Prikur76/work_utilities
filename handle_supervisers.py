
import httpx
import pandas as pd
import gspread
import logging

from environs import Env
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

from app_logger import get_logger
from tools import format_date_string
from settings import (
    SPREADSHEET_NAME, WORKSHEET_NAME, 
    GOOGLE_SHEETS_CREDENTIALS_FILE, 
    USER, PASSWORD, DRIVERS_URL
)

logger = get_logger(__name__)


# Подключение к Google Sheets
def connect_to_google_sheets():
    """Подключение к Google Sheets"""
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            GOOGLE_SHEETS_CREDENTIALS_FILE, 
            scope
        )
        client = gspread.authorize(credentials)
        logging.info("Успешное подключение к Google Sheets")
        return client
    except Exception as e:
        logging.error("Ошибка подключения к Google Sheets: %s", e)
        raise

# Получение данных из 1С
def fetch_data_from_1c():
    """Получение данных из 1С"""
    with httpx.Client() as client:
        response = client.get(
            DRIVERS_URL,
            auth=(USER, PASSWORD),
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        response.raise_for_status()
        return response.json()


# Обработка данных
def process_data(data):
    df = pd.DataFrame(data)
    
    # Словарь соответствия старых и новых названий столбцов
    rename_columns = {
        "ID": "Идентификатор",
        "FIO": "ФИО",
        "PhoneNumber": "Номер телефона",
        "DriverDateCreate": "Дата создания",
        "Status": "Статус",
        "Comment": "Комментарий",
        "Supervisor": "Куратор"
    }
    
    # Применяем переименование
    df = df.rename(columns=rename_columns)
    
    # Продолжаем обработку
    filters = (df["Куратор"] != "") & (df["Дата создания"] > "2023-12-31T23:59:59")
    df_filtered = df[filters].copy().reset_index(drop=True)
    
    df_filtered["Год-мес"] = df_filtered["Дата создания"].apply(
        lambda x: datetime.fromisoformat(x).strftime("%Y-%m")  if pd.notnull(x) else None
    )
    df_filtered["Дата создания"] = df_filtered["Дата создания"].apply(
        lambda x: datetime.fromisoformat(x).strftime("%Y-%m-%d") if pd.notnull(x) else None
    )
    
    # Выбор нужных столбцов с новыми названиями
    required_columns = [
        "Идентификатор",
        "ФИО",
        "Номер телефона",
        "Дата создания",
        "Год-мес",
        "Статус",
        "Куратор",
        "Комментарий"
    ]
    
    # Проверяем наличие всех колонок
    for col in required_columns:
        if col not in df_filtered.columns:
            df_filtered[col] = None
    
    return df_filtered.sort_values("Идентификатор", ascending=False)[required_columns]


# Запись данных в Google Sheets
def write_to_google_sheets(df, client):
    spreadsheet = client.open(SPREADSHEET_NAME)
    worksheet = spreadsheet.worksheet(WORKSHEET_NAME)
    
    # Преобразуем DataFrame в список списков (включая заголовки)
    data = [df.columns.values.tolist()]  # Заголовки
    data += df.values.tolist()           # Данные
    
    # Очищаем лист и записываем все данные одним запросом
    worksheet.clear()
    worksheet.update(values=data, range_name='B1', value_input_option="USER_ENTERED")  # Запись начинается с ячейки B1


# Основная функция
def update_supervisers():
    try:
        logging.info("***** START *****")

        # Шаг 1: Получение данных из 1С
        data = fetch_data_from_1c()
        
        # Шаг 2: Обработка данных
        df = process_data(data)
      
        # Шаг 3: Подключение к Google Sheets
        client = connect_to_google_sheets()
        
        # Шаг 4: Запись данных в Google Sheets
        write_to_google_sheets(df, client)
        
        logging.info("***** DONE SUCCESSFULLY *****")
    except Exception as e:
        logging.error("***** CRITICAL ERROR: %s *****", e)
        raise