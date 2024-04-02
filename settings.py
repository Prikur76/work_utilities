from environs import Env

env = Env()
env.read_env()


USER = env.str('ELEMENT_LOGIN')
PASSWORD = env.str('ELEMENT_PASSWORD')

DRIVERS_URL = env.str('ELEMENT_DRIVERS_URL')
CARS_URL = env.str('ELEMENT_CARS_URL')

DRIVERS_RANGE_FOR_UPDATE = env.str('RANGE_DRIVERS_FOR_UPDATE')
CARS_RANGE_FOR_UPDATE = env.str('RANGE_CARS_FOR_UPDATE')

MSK_PARKS = {
    'region': env.str('MSK_REGION'),
    'yandex': [
        {
            'park_id': env.str('MSK_PARK_ID'),
            'api_key': env.str('MSK_X_API_KEY'),
        },
        {
            'park_id': env.str('SPECIAL_PARK_ID'),
            'api_key': env.str('SPECIAL_X_API_KEY'),
        },
        {
            'park_id': env.str('ELS_PARK_ID'),
            'api_key': env.str('ELS_X_API_KEY'),
        },
    ],
    'sheets_ids': env.list('MSK_SPREADSHEET_ID'),
}

EKAT_PARKS = {
    'region': env.str('EKB_REGION'),
    'yandex': [
        {
            'park_id': env.str('EKB_PARK_ID'),
            'api_key': env.str('EKB_X_API_KEY'),
        },
    ],
    'sheets_ids': env.list('EKB_SPREADSHEET_ID'),
}

CHLB_PARKS = {
    'region': env.str('CHLB_REGION'),
    'yandex': [
        {
            'park_id': env.str('CHLB_PARK_ID'),
            'api_key': env.str('CHLB_X_API_KEY'),
        },
    ],
    'sheets_ids': env.list('CHLB_SPREADSHEET_ID'),
}

YAR_PARKS = {
    'yandex': [
        {
            'park_id': env.str('YAR_PARK_ID'),
            'api_key': env.str('YAR_X_API_KEY'),
        },
    ],
    'sheets_ids': env.list('YAR_SPREADSHEET_ID'),
    'region': env.str('YAR_REGION'),
}

REPORTS_SHEETS_IDS = env.list('REPORTS_SPREADSHEETS_IDS')

EXCLUDE_ROSTER = ['', 'Комфорт', 'Штатный',
                  'Подключашки 2 %', 'ПОДКЛЮЧАШКА 3%']
