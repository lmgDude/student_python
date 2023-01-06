from prettytable import PrettyTable
import csv
import re
import os


def convert_bool(value):
    return "Да" if value == "True" else "Нет"


def convert_bool_reverse(value):
    return True if value == "Да" else False


def convert_tax(bool_value):
    return "С вычетом налогов" if bool_value.lower() != "да" else "Без вычета налогов"


def fix_salary(salary):
    return (salary.replace('.0', '')[:-3] + ' ' + salary.replace('.0', '')[-3:]).lstrip()


def fix_field(field):
    return ' '.join(re.sub(re.compile(r'<[^>]+>'), '', field).split())


def get_date(datetime):
    return ".".join(reversed(datetime[:datetime.index('T')].split('-')))


def line_trim(vacancy, attr):
    return getattr(vacancy, attr)[:100] + '...' if len(getattr(vacancy, attr)) > 100 else getattr(vacancy, attr)[:100]


class DataSet:
    def __init__(self, file_name):
        self.file_name = file_name
        self.salary_keys = ['salary_from', 'salary_to', 'salary_gross', 'salary_currency']
        self.vacancy_keys = ['name', 'description', 'key_skills', 'experience_id', 'premium', 'employer_name',
                             object, 'area_name', 'published_at']

    def csv_reader(self):
        with open(self.file_name, encoding='utf-8-sig') as file:
            return [row for row in csv.DictReader(file)]

    def csv_filer(self):
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
    def __init__(self, name, description, key_skills, experience_id, premium,
                 employer_name, salary, area_name, published_at):
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
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

    def converter(self, salary_currency):
        currency_key = ["Манаты", "Белорусские рубли", "Евро", "Грузинский лари", "Киргизский сом", "Тенге", "Рубли",
                        "Гривны", "Доллары", "Узбекский сум"]
        currency_value = [35.68, 23.91, 59.00, 21.74, 0.76, 0.13, 1, 1.64, 60.66, 0.0055]
        currency_dict = dict(zip(currency_key, currency_value))
        return (int(self.salary_to.replace('.0', '')) + int(self.salary_from.replace('.0', ''))) // 2 \
               * currency_dict[salary_currency]


class InputConect:
    def __init__(self):
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
    data_vacancies = InputConect()
    data_vacancies.process_data()
    if data_vacancies.is_correct_parameters:
        data_vacancies.print_vacancies()
