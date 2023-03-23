#!/home/vlad/environments/work_utilities/bin/python

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
        r'^(\+7|7|8)?[\s\-]?\(?[9][0-9]{2}\)?'
        r'[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',
        phone.strip()
    )
    return bool(result)
