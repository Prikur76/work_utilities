import logging
import os

from dotenv import load_dotenv
import yandex as ya

logger = logging.getLogger(__name__)

"""
Сценарий:
1. ивзлекаем данные из источников(Яндекс, 1с): водители, условия работы, машины
2. производим объединение таблиц
3. Объединение данных в 1 датафрейм
4. выбираем поля
"""

def main():
    logging.basicConfig(
        format='[%(levelname)s] - %(asctime)s - %(name)s - %(message)s',
        level=logging.INFO
    )
    load_dotenv()
    # ss_id =  os.environ.get('SPREADSHEET_ID')
    # login_1c = os.environ.get('LOGIN_1C')
    # password_1c = os.environ.get('PASSWORD_1C')
    # drivers_1c_url = os.environ.get('DRIVERS_1C_URL')

    ekb_park_id = os.environ.get('EKB_PARK_ID')
    ekb_api_key = os.environ.get('EKB_X_API_KEY')

    krv_park_id = os.environ.get('KRV_PARK_ID')
    krv_api_key = os.environ.get('KRV_X_API_KEY')

    ekb = ya.Taximeter(ekb_park_id, ekb_api_key)
    # ekb_drivers = ekb.fetch_drivers_profiles()
    # print(len(ekb_drivers))
    # ekb_cars = ekb.fetch_cars()
    # print(len(ekb_cars))

    krv = ya.Taximeter(krv_park_id, krv_api_key)
    # krv_drivers = krv.fetch_drivers_profiles()
    # print(len(krv_drivers))
    # krv_wrs = krv.fetch_workrules()
    # print(krv_wrs)


if __name__ == '__main__':
    main()
