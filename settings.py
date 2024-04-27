from environs import Env

env = Env()
env.read_env()


USER = env.str('ELEMENT_LOGIN')
PASSWORD = env.str('ELEMENT_PASSWORD')
DRIVERS_URL = env.str('ELEMENT_DRIVERS_URL')
CARS_URL = env.str('ELEMENT_CARS_URL')
REPORT_ID = env.str('REPORT_SPREADSHEETS_ID')
RANGE_FOR_UPLOAD = env.str('RANGE_FOR_UPLOAD')

EXCLUDE_ROSTER = ['', 'Комфорт', 'Штатный',
                  'Подключашки 2 %', 'ПОДКЛЮЧАШКА 3%']
