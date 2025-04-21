from environs import Env

env = Env()
env.read_env()


USER = env.str('ELEMENT_LOGIN')
PASSWORD = env.str('ELEMENT_PASSWORD')
DRIVERS_URL = env.str('ELEMENT_DRIVERS_URL')
CARS_URL = env.str('ELEMENT_CARS_URL')
REPORT_ID = env.str('REPORT_SPREADSHEETS_ID')
RANGE_FOR_UPLOAD = env.str('RANGE_FOR_UPLOAD')
RANGE_FOR_UPLOAD_DRIVERS = env.str('RANGE_FOR_UPLOAD_DRIVERS')
RANGE_FOR_SELFEMPLOYED = env.str('RANGE_FOR_SELFEMPLOYED')

EXCLUDE_ROSTER = ['', 'Комфорт', 'Штатный',
                  'Подключашки 2 %', 'ПОДКЛЮЧАШКА 3%']

PARKS = [
    {
        'city': 'МОСКВА',
        'id': env.str('MSK_PARK_ID'),
        'api_key': env.str('MSK_X_API_KEY')
    },
    {
        'city': 'МОСКВА (СОЦИАЛЬНЫЙ)',
        'id': env.str('SPECIAL_PARK_ID'),
        'api_key': env.str('SPECIAL_X_API_KEY')
    },
    {
        'city': 'МОСКВА',
        'id': env.str('ELS_PARK_ID'),
        'api_key': env.str('ELS_X_API_KEY')
    },
    {
        'city': 'Екатеринбург',
        'id': env.str('EKB_PARK_ID'),
        'api_key': env.str('EKB_X_API_KEY')
    },
    {
        'city': 'Ярославль',
        'id': env.str('YAR_PARK_ID'),
        'api_key': env.str('YAR_X_API_KEY')
    },
    {
        'city': 'ЧЕЛЯБИНСК',
        'id': env.str('CHL_PARK_ID'),
        'api_key': env.str('CHL_X_API_KEY')
    }
]


GOOGLE_SHEETS_CREDENTIALS_FILE = env.str("GOOGLE_SHEETS_CREDENTIALS_FILE", "")
SPREADSHEET_NAME = env.str("SPREADSHEET_NAME")
WORKSHEET_NAME = env.str("WORKSHEET_NAME")  