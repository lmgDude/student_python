from prettytable import PrettyTable
import csv
import re
import os
import doctest
from datetime import datetime


def convert_bool(value):
    """Конвертирует булевое значение в текст
    :param value: (str) Булевое значение
    :return: (str) Конвертированный текст
    >>> convert_bool("True")
    'Да'
    >>> convert_bool("False")
    'Нет'
    """
    return "Да" if value == "True" else "Нет"


def convert_bool_reverse(value):
    """Конвертирует текст в булевое значение
    :param value: (str) текст
    :return: (bool) конвертированное булевое значение
    >>> convert_bool_reverse("Да")
    True
    >>> convert_bool_reverse("Нет")
    False
    """
    return True if value == "Да" else False


def convert_tax(bool_value):
    """Конвертирует слова (да/нет) в (с вычетом налогов/без вычета налогов)
    :param bool_value: (str) слова да или нет
    :return: (str) полученный текст
    >>> convert_tax('да')
    'Без вычета налогов'
    >>> convert_tax('нет')
    'С вычетом налогов'
    """
    return "С вычетом налогов" if bool_value.lower() != "да" else "Без вычета налогов"


def fix_salary(salary):
    """Функция для отделения ноликов у многозначных чисел (12000 -> 12 000).
    :param salary: (str) Значение оклада
    :return: (str) Пофиксенное значение оклада
    >>> fix_salary("1000")
    '1 000'
    >>> fix_salary("100")
    '100'
    >>> fix_salary("55000")
    '55 000'
    """
    return (salary[:-3] + ' ' + salary[-3:]).lstrip()


def fix_field(field):
    """Убирает из строки все HTML тэги
    :param field: (str) строка с html тэгами
    :return: (str) строка без html тэгов
    >>> fix_field("<p>Контур<strong>")
    'Контур'
    >>> fix_field("<p><strong>«АйДи-360»</strong> ")
    '«АйДи-360»'
    >>> fix_field("<p><strong>Основные функции:</strong></p> <ul>")
    'Основные функции:'
    """
    return ' '.join(re.sub(re.compile(r'<[^>]+>'), '', field).split())


def get_date(date_original):
    """Возвращает из строки с датой и временем только дату
    :param date_original: (str) строка с датой и временем
    :return: (str) дата
    >>> get_date("2022-07-05T18:22:28+0300")
    '05.07.2022'
    >>> get_date("2022-07-18T05:14:45+0300")
    '18.07.2022'
    >>> get_date("2022-12-03T19:16:33+0300")
    '03.12.2022'
    """

    """Старый код
    return ".".join(reversed(datetime[:datetime.index('T')].split('-')))
    """

    new_date = datetime.strptime(date_original[:-5], '%Y-%m-%dT%H:%M:%S')
    return str(new_date.date())


def line_trim(vacancy, attr):
    """Если в тексте ячейки вакансии больше 100 символов, то возвращает обрезанную до 100 символов строку
    :param vacancy: (dict) вакансия
    :param attr: (value of dict, string) ячейка вакансии
    :return:
    >>> long_vac = Vacancy(1, "Системное мышление, Холодные продажи, Деловое общение, Продажа комплексных проектов, Тайм-менеджмент, Перевод текстов", "1", 1, 1, 1, 1, 1, 1)
    >>> line_trim(long_vac, 'description')
    'Системное мышление, Холодные продажи, Деловое общение, Продажа комплексных проектов, Тайм-менеджмент...'
    >>> small_vac = Vacancy(1, "Строка с количеством символов меньше 100", "1", 1, 1, 1, 1, 1, 1)
    >>> line_trim(small_vac, 'description')
    'Строка с количеством символов меньше 100'
    """
    return getattr(vacancy, attr)[:100] + '...' if len(getattr(vacancy, attr)) > 100 else getattr(vacancy, attr)[:100]


class DataSet:
    """Класс для предоставления коллекции корректных вакансий
    Attributes:
        file_name (str): название файла
    """

    def __init__(self, file_name):
        """Инициализирует объект DataSet
        :param file_name: (str) название файла
        >>> data = DataSet("vacancies.csv")
        >>> data.file_name
        'vacancies.csv'
        """

        self.file_name = file_name
        self.salary_keys = ['salary_from', 'salary_to', 'salary_gross', 'salary_currency']
        self.vacancy_keys = ['name', 'description', 'key_skills', 'experience_id', 'premium', 'employer_name',
                             object, 'area_name', 'published_at']

    def csv_reader(self):
        """Возвращает словарь со всеми вакансиями из файла self.file_name
        :return: (dict) словарь
        >>> data = DataSet("vacancies.csv")
        >>> type(data.csv_reader()[0]).__name__
        'dict'
        """
        with open(self.file_name, encoding='utf-8-sig') as file:
            return [row for row in csv.DictReader(file)]

    def csv_filer(self):
        """Возвращает словарь объектов Vacancy только с корректными значениями из всего начального словаря
        :return: (dict) корректный словарь
        >>> data = DataSet("vacancies.csv")
        >>> type(data.csv_filer()[0]).__name__
        'Vacancy'
        """
        vacancies_objects = list()
        for row in DataSet.csv_reader(self):
            correct_row = True
            for field in row:
                if row[field] is None or len(row[field]) == 0:
                    correct_row = False
                    continue
            if correct_row:
                salary = Salary(*[row[key] for key in self.salary_keys])
                vacancy = Vacancy(*[row[key] if key != object else salary for key in self.vacancy_keys])
                vacancies_objects.append(vacancy)
        return vacancies_objects if len(vacancies_objects) != 0 else False


class Vacancy:
    """Класс для предоставления вакансии
    Attributes:
        name (str): название вакансии
        description (str): описание вакансии
        key_skills (str[]): требуемые навыки
        experience_id (str): опыт работы
        premium (str): является ли профессия премиумной
        employer_name (str): название компании
        salary (Salary): оклад
        area_name (str): название региона
        published_at (str): дата и время публикации
    """

    def __init__(self, name, description, key_skills, experience_id, premium,
                 employer_name, salary, area_name, published_at):
        """Инициализирует объект Vacancy
        :param name: (str) название вакансии
        :param description: (str) описание вакансии
        :param key_skills: (str) требуемые навыки
        :param experience_id: (str) опыт работы
        :param premium: (str) является ли профессия премиумной
        :param employer_name: (str) название компании
        :param salary: (Salary) оклад
        :param area_name: (str) название региона
        :param published_at: (str) дата и время публикации
        >>> vac = Vacancy("1<i>", "1<i>", "1\\n2", "between3And6", "True", 1, Salary(10000, 30000, "True", "EUR"), 1, 1)
        >>> type(vac).__name__
        'Vacancy'
        >>> vac.name
        '1<i>'
        >>> vac.description
        '1<i>'
        >>> vac.key_skills
        ['1', '2']
        >>> vac.experience_id
        'between3And6'
        >>> vac.premium
        'True'
        >>> vac.employer_name
        1
        >>> type(vac.salary).__name__
        'Salary'
        >>> vac.area_name
        1
        >>> vac.published_at
        1
        """
        self.name = name
        self.description = description
        self.key_skills = key_skills.split('\n')
        self.experience_id = experience_id
        self.premium = premium
        self.employer_name = employer_name
        self.salary = salary
        self.area_name = area_name
        self.published_at = published_at

    def formatter(self):
        """Конвертирует и переводит на русский язык поля с помощью словарей - currency_dict и experience_dict
        и других функций
        >>> vac = Vacancy("1<i>", "1<i>", "1\\n2", "between3And6", "True", 1, Salary(10000, 30000, "True", "EUR"), 1, 1)
        >>> vac.formatter()
        >>> vac.salary.salary_currency
        'Евро'
        >>> vac.experience_id
        'От 3 до 6 лет'
        >>> vac.description
        '1'
        >>> vac.name
        '1'
        >>> vac.premium
        'Да'
        >>> vac.salary.salary_gross
        'Да'
        """

        currency_key_eng = ['AZN', 'BYR', 'EUR', 'GEL', 'KGS', 'KZT', 'RUR', 'UAH', 'USD', 'UZS']
        currency_key_rus = ["Манаты", "Белорусские рубли", "Евро", "Грузинский лари", "Киргизский сом", "Тенге",
                            "Рубли", "Гривны", "Доллары", "Узбекский сум"]

        experience_key_eng = ["noExperience", "between1And3", "between3And6", "moreThan6"]
        experience_key_rus = ["Нет опыта", "От 1 года до 3 лет", "От 3 до 6 лет", "Более 6 лет"]

        currency_dict = dict(zip(currency_key_eng, currency_key_rus))
        experience_dict = dict(zip(experience_key_eng, experience_key_rus))

        self.salary.salary_currency = currency_dict[self.salary.salary_currency]
        self.experience_id = experience_dict[self.experience_id]
        self.description = fix_field(self.description)
        self.name = fix_field(self.name)
        self.premium = convert_bool(self.premium)
        self.salary.salary_gross = convert_bool(self.salary.salary_gross)


class Salary:
    """Класс для предоставления зарплаты
    Attributes:
        salary_from (int): нижняя граница вилки оклада
        salary_to (int): верхняя граница вилки оклада
        salary_currency (str): валюта оклада
        salary_gross (str): оклад указан до вычета налогов
    """

    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        """Инициализирует объект Salary
        :param salary_from: (int) нижняя граница вилки оклада
        :param salary_to: (int) верхняя граница вилки оклада
        :param salary_gross: (str) оклад указан до вычета налогов
        :param salary_currency: (str) валюта оклада
        >>> salary = Salary(10000, 30000, "True", "RUR")
        >>> type(salary).__name__
        'Salary'
        >>> salary.salary_from
        10000
        >>> salary.salary_to
        30000
        >>> salary.salary_gross
        'True'
        >>> salary.salary_currency
        'RUR'
        """
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

    def converter(self, salary_currency):
        """ Вычисляет среднюю зарплату и переводит ее в рубли с помощью словаря - currency_dict
        :param salary_currency: (str) валюта оклада
        :return: (int) средняя зарплата в рублях
        >>> salary = Salary("10000", "30000", "True", "Тенге")
        >>> salary.converter(salary.salary_currency)
        2600
        >>> salary = Salary("10000", "30000", "True", "Рубли")
        >>> salary.converter(salary.salary_currency)
        20000
        """
        currency_key = ["Манаты", "Белорусские рубли", "Евро", "Грузинский лари", "Киргизский сом", "Тенге", "Рубли",
                        "Гривны", "Доллары", "Узбекский сум"]
        currency_value = [35.68, 23.91, 59.00, 21.74, 0.76, 0.13, 1, 1.64, 60.66, 0.0055]
        currency_dict = dict(zip(currency_key, currency_value))

        return int((int(self.salary_to) + int(self.salary_from)) // 2 * currency_dict[salary_currency])


class InputConect:
    """Отвечает за обработку параметров вводимых пользователем: фильтры, сортировка, диапазон вывода,
    требуемые столбцы, а также за печать таблицы на экран
    Attributes:
        file_name (str): название файла
        filter_string (str): параметр фильтрации
        sort_string (str): параметр сортировки
        reverse_sort (str): обратный порядок сортировки
        numbers (int, int): диапазон вывода
        skills (str[]): требуемые для вывода столбцы
        is_correct_parameters (bool): корректны ли введенные выше параметры или нет
        data_vacancies (dict): словарь корректных вакансий
        keys (str[]): названия столбцов итоговой таблицы
    """

    def __init__(self):
        """Инициализация объекта InputConect"""
        self.file_name = input("Введите название файла: ")
        self.filter_string = input("Введите параметр фильтрации: ")
        self.sort_string = input("Введите параметр сортировки: ")
        self.reverse_sort = input("Обратный порядок сортировки (Да / Нет): ")
        self.numbers = input("Введите диапазон вывода: ")
        self.skills = input("Введите требуемые столбцы: ")
        self.is_correct_parameters = False
        self.data_vacancies = []
        self.keys = ["Название", "Описание", "Навыки", "Опыт работы", "Премиум-вакансия", "Компания",
                     "Оклад", "Название региона", "Дата публикации вакансии", "Идентификатор валюты оклада", ]

    def process_data(self):
        """Обработка введенных параметров на корректность
        :return: устанавливаются значения is_correct_parameters объекта и data_vacancies, либо в консоль выводится
        сообщение об ошибке
        """
        if os.stat(self.file_name).st_size == 0:
            print("Пустой файл")
        elif ':' not in self.filter_string and self.filter_string != "":
            print("Формат ввода некорректен")
        elif self.filter_string.split(": ")[0] not in self.keys and self.filter_string.split(": ")[0] != "":
            print("Параметр поиска некорректен")
        elif self.sort_string not in self.keys and self.sort_string != "":
            print("Параметр сортировки некорректен")
        elif self.reverse_sort not in ["Да", "Нет", ""]:
            print("Порядок сортировки задан некорректно")
        else:
            self.is_correct_parameters = True
            self.data_vacancies = DataSet(self.file_name).csv_filer()

    def print_vacancies(self):
        """Печатает в консоль полученную таблицу с учетом всех введенных пользователем параметров.
        1) Устанавливаются параметры выводимой таблицы.
        2) Поля вакансии в коллекции вакансий конвертируются с помощью метода formatter
        3) Коллекция вакансий сортируется по параметру sort_string
        4) Создается и заполняется новая коллекция вакансий, вакансии которой прошли фильтрацию основной коллекции
        5) Выводится таблица с учетом содержимого параметров numbers и skills
        :return: (Prettytable) таблица
        """
        usual_tags = ["Дата публикации вакансии", "Опыт работы", "Премиум-вакансия", "Название региона",
                      "Компания", "Название", "Описание"]
        tags = ["Название", "Описание", "Навыки", "Опыт работы", "Премиум-вакансия", "Компания", "Оклад",
                "Название региона", "Дата публикации вакансии"]
        translate_tags = ["name", "description", "key_skills", "experience_id", "premium", "employer_name",
                          "salary_all", "area_name", "published_at"]
        translate_dict = dict(zip(tags, translate_tags))

        vacancy_table = PrettyTable()
        vacancy_table.hrules = 1
        vacancy_table.align = "l"
        vacancy_table.field_names = ["№"] + tags
        vacancy_table._max_width = {field: 20 for field in vacancy_table.field_names}

        filter_string = self.filter_string.split(": ")
        numbers_none = len(self.numbers) == 0
        skills_none = len(self.skills) == 0

        if not self.data_vacancies:
            print("Нет данных")
            return
        else:
            [vacancy.formatter() for vacancy in self.data_vacancies]
            if self.sort_string == "":
                pass
            elif self.sort_string == "Навыки":
                self.data_vacancies.sort(key=lambda vacancy: len(vacancy.key_skills),
                                         reverse=convert_bool_reverse(self.reverse_sort))
            elif self.sort_string == "Оклад":
                self.data_vacancies.sort(key=lambda vacancy: vacancy.salary.converter(vacancy.salary.salary_currency),
                                         reverse=convert_bool_reverse(self.reverse_sort))
            elif self.sort_string == "Опыт работы":
                self.data_vacancies.sort(key=lambda vacancy: vacancy.experience_id[3],
                                         reverse=convert_bool_reverse(self.reverse_sort))
            else:
                self.data_vacancies.sort(key=lambda vacancy: getattr(vacancy, translate_dict[self.sort_string]),
                                         reverse=convert_bool_reverse(self.reverse_sort))

            new_data_vacancies = []
            for vacancy in self.data_vacancies:
                vacancy.published_at = get_date(vacancy.published_at)
                vacancy.key_skills = "\n".join(vacancy.key_skills)
                if filter_string[0] == "" or (filter_string[0] in usual_tags and
                                              filter_string[1] == getattr(vacancy, translate_dict[filter_string[0]])):
                    new_data_vacancies.append(vacancy)
                else:
                    if filter_string[0] == "Навыки":
                        if set(filter_string[1].split(", ")).issubset(getattr(vacancy, translate_dict[filter_string[0]])
                                                                              .split("\n")):
                            new_data_vacancies.append(vacancy)
                    elif filter_string[0] == "Оклад":
                        if int(vacancy.salary.salary_from) <= int(filter_string[1]) <= int(vacancy.salary.salary_to):
                            new_data_vacancies.append(vacancy)
                    elif filter_string[0] == "Идентификатор валюты оклада":
                        if vacancy.salary.salary_currency == filter_string[1]:
                            new_data_vacancies.append(vacancy)

            for vacancy in new_data_vacancies:
                vacancy.salary = f"{fix_salary(vacancy.salary.salary_from)} - " \
                                 f"{fix_salary(vacancy.salary.salary_to)}" \
                                 f" ({vacancy.salary.salary_currency}) ({convert_tax(vacancy.salary.salary_gross)})"
                vacancy_table.add_row([new_data_vacancies.index(vacancy) + 1] +
                                      [line_trim(vacancy, attr) for attr in vars(vacancy).keys()])

        if not numbers_none and not skills_none:
            numbers = self.numbers.split()
            if len(numbers) == 1:
                vacancy_table = vacancy_table.get_string(start=int(numbers[0]) - 1,
                                                         fields=['№'] + self.skills.split(', '))
            else:
                vacancy_table = vacancy_table.get_string(start=int(numbers[0]) - 1, end=int(numbers[1]) - 1,
                                                         fields=['№'] + self.skills.split(', '))

        if not numbers_none and skills_none:
            numbers = self.numbers.split()
            if len(numbers) == 1:
                vacancy_table = vacancy_table.get_string(start=int(numbers[0]) - 1)
            else:
                vacancy_table = vacancy_table.get_string(start=int(numbers[0]) - 1, end=int(numbers[1]) - 1)

        if numbers_none and not skills_none:
            vacancy_table = vacancy_table.get_string(fields=['№'] + self.skills.split(', '))

        if len(new_data_vacancies) == 0:
            print("Ничего не найдено")
        else:
            print(vacancy_table)


def execute():
    """Функция для выполнения программы"""
    data_vacancies = InputConect()
    data_vacancies.process_data()
    if data_vacancies.is_correct_parameters:
        data_vacancies.print_vacancies()


if __name__ == "__main__":
    doctest.testmod()