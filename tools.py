import re
import textwrap as tw
from datetime import datetime


def remove_chars(s):
    return re.sub(r'[^0-9a-zA-Zа-яА-Яё]+', ' ', s)


def create_passport(number, issue_date, department, code):
    """Создает строку с данными паспорта"""
    passport = ''
    if number or department or code:
        passport = """паспорт: %s, выдан %s, орган: %s, код: %s""" \
                   % (number, issue_date, department, code)
    return tw.dedent(passport)


def create_contract(begin_date, end_date):
    """Создает строку с данными договора с водителем"""
    contract = ''
    if begin_date or end_date:
        contract = """начат: %s, окончание: %s""" \
                   % (begin_date, end_date)
    return tw.dedent(contract)


def format_date_string(date_string, format='%d.%m.%Y'):
    """Форматирует строку с датой в формат даты"""
    old_format = datetime.strptime(
        date_string, '%Y-%m-%dT%H:%M:%S')
    new_format = old_format.strftime(format)
    return new_format


def check_phone(phone):
    """Возвращает True or False как результат проверки соответствия
    маске мобильного телефона
    """
    result = re.match(
        r"^(\+7|7|8)?[\s\-]?\(?9[0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$",
        phone.strip()
    )
    return bool(result)


def format_driver_info(row_data):
    """Возвращает строку с информацией о водителе"""
    control_date = datetime.strptime(row_data['DatePL'], '%Y-%m-%d').strftime('%d.%m.%Y') \
        if row_data['DatePL'] != '0001-01-01' else 'нет даты'
    driver_info = """\
        %s
        тел.: %s
        усл.: %s
        контроль: %s""" % (row_data['FIO'], row_data['PhoneNumber'],
                           row_data['NameConditionWork'], control_date)
    return tw.dedent(driver_info)


def format_car_info(row_data):
    """Возвращает строку с детальной информацией о машине"""
    car_info = """\
        %s (%s)
        vin: %s
        гнз: %s
        %s""" % (row_data['Model'], row_data['YearCar'], row_data['VIN'],
                          row_data['Number'], row_data['Transmission'])
    if row_data['GBO']:
        car_info += """, ГБО"""
    return tw.dedent(car_info)


def format_status_detail(row_data):
    """Возвращает строку с детальной информацией по статусу машины"""
    status_detail = ''
    if row_data['Status']:
        status_detail = """%s\n""" % row_data['Status']
    if row_data['Reason']:
        status_detail += """\nпричина: %s""" % row_data['Reason']
    return tw.dedent(status_detail)


def format_dc_detail(row_data):
    """Возвращает строку с информацией о диагностической карте"""
    if row_data['TOSeriesNumber']:
        dc_date = datetime.strptime(
            row_data['TOIssueDate'], '%Y-%m-%dT%H:%M:%S')\
            .strftime('%d.%m.%Y')
        dc_detail = """ДК %s от %s""" % (row_data['TOSeriesNumber'], dc_date)
        return tw.dedent(dc_detail)


def format_osago_detail(row_data):
    """Возвращает строку с информацией о ОСАГО"""
    if row_data['OSAGOSeriesNumber']:
        osago_date = datetime.strptime(
            row_data['OSAGOIssueDate'], '%Y-%m-%dT%H:%M:%S')\
            .strftime('%d.%m.%Y')
        osago_detail = """\
        Полис ОСАГО
        %s
        от %s""" % (row_data['OSAGOSeriesNumber'], osago_date)
        return tw.dedent(osago_detail)


def format_license_detail(row_data):
    """Возвращает строку с информацией о лицензии"""
    if row_data['LicenseSeriesNumber']:
        license_date = datetime.strptime(
            row_data['LicenseIssueDate'], '%Y-%m-%dT%H:%M:%S')\
            .strftime('%d.%m.%Y')
        license_detail = """\
        Реестр N %s
        от %s""" % (row_data['LicenseSeriesNumber'], license_date)
        return tw.dedent(license_detail)


def format_sts_detail(row_data):
    """Возвращает строку с информацией о СТС"""
    if row_data['STSSeriesNumber']:
        sts_date = datetime.strptime(
            row_data['STSIssueDate'],'%Y-%m-%dT%H:%M:%S')\
            .strftime('%d.%m.%Y')
        sts_detail = """\
        СТС %s
        от %s""" % (row_data['STSSeriesNumber'], sts_date)
        return tw.dedent(sts_detail)
