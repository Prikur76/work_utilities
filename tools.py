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
    driver_info = ''
    if row_data['FIO']:
        try:
            if '0001-01-01' in row_data['DatePL']:
                pl_date = 'нет даты'
            else:
                pl_date = datetime\
                    .strptime(row_data['DatePL'], '%Y-%m-%d')\
                    .strftime('%d.%m.%Y')
        except ValueError:
            pl_date = 'нет даты'
        balance = '0 руб.'
        if row_data['Balance'] == 0.0:
            balance = '0 руб.'
        else:
            balance = str(row_data['Balance']).replace('.', ',') + ' руб.'
        driver_info = """\
            %s
            тел.: %s
            баланс: %s
            усл.: %s
            контроль: %s""" % (row_data['FIO'], row_data['PhoneNumber'],
                                balance, row_data['NameConditionWork'], pl_date)
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
    dc_detail = ''
    if row_data['TOSeriesNumber']:
        try:
            dc_date = format_date_string(row_data['TOIssueDate'])
        except ValueError:
            dc_date = ''
        dc_detail = """ДК %s от %s""" % (row_data['TOSeriesNumber'], dc_date)
    return tw.dedent(dc_detail)


def format_osago_detail(row_data):
    """Возвращает строку с информацией о ОСАГО"""
    osago_detail = ''
    if row_data['OSAGOSeriesNumber']:
        try:
            osago_date = format_date_string(row_data['OSAGOIssueDate'])
        except ValueError:
            osago_date = ''
        osago_detail = """\
        Полис ОСАГО
        %s
        от %s""" % (row_data['OSAGOSeriesNumber'], osago_date)
    return tw.dedent(osago_detail)


def format_license_detail(row_data):
    """Возвращает строку с информацией о лицензии"""
    license_detail = ''
    if row_data['LicenseSeriesNumber']:
        try:
            license_date = format_date_string(row_data['LicenseIssueDate'])
        except ValueError:
            license_date = ''
        license_detail = """\
        Реестр N %s
        от %s""" % (row_data['LicenseSeriesNumber'], license_date)
    return tw.dedent(license_detail)


def format_sts_detail(row_data):
    """Возвращает строку с информацией о СТС"""
    sts_detail = ''
    if row_data['STSSeriesNumber']:
        try:
            sts_date = format_date_string(row_data['STSIssueDate'])
        except ValueError:
            sts_date = ''
        sts_detail = """\
        СТС %s
        от %s""" % (row_data['STSSeriesNumber'], sts_date)
    return tw.dedent(sts_detail)


# Группа функций для обработки данных водителей
def clean_phone(row_data):
    """Возвращает строку с телефонами водителя или False"""
    clean_data = re.sub(r'[^0-9]+', ' ', row_data)
    clean_phone = ', '.join(
        re.findall(r'([\+7|8|7]+[0-9]{10})',
                   clean_data)
    )
    if not clean_phone:
        return None, False
    return clean_phone, True


def format_driver_phones(row_data):
    """Возвращает строку с телефонами водителя"""
    driver_phones = ''
    main_phone, main_status = clean_phone(row_data['PhoneNumber'])
    additional_phone, add_status = clean_phone(row_data['PhoneNumber2'])
    if main_status:
        driver_phones ="""осн.: %s""" % main_phone
    if add_status:
        driver_phones += """\nдоп.: %s""" % additional_phone
    return tw.dedent(driver_phones)


def format_passport_info(row_data):
    """Возвращает строку с данными паспорта"""
    passport_info = ''
    if row_data['PassportSerialNumber']:
        passport_info = """\
        паспорт %s выдан %s %s""" % (row_data['PassportSerialNumber'],
                                     format_date_string(row_data['PassportIssueDate']),
                                     row_data['PassportDepartmentName'].upper())
    return tw.dedent(passport_info)


def format_driver_license(row_data):
    """Возвращает строку с данными вод. удостоверения"""
    driver_license = ''
    if row_data['DriversLicenseSerialNumber']:
        driver_license = """\
        ВУ %s
        выдано %s
        действует до %s
        """ % (row_data['DriversLicenseSerialNumber'],
                              format_date_string(row_data['DriversLicenseIssueDate']),
                              format_date_string(row_data['DriversLicenseExpiryDate']))
        if '0001-01-01' not in row_data['DriversLicenseExperienceTotalSince']:
            driver_license += """стаж c %s""" % format_date_string(
                row_data['DriversLicenseExperienceTotalSince'])
    return tw.dedent(driver_license)

