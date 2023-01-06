from unittest import TestCase
from statistic import *


class FunctionsTests(TestCase):
    def test_convert_bool(self):
        self.assertEqual(convert_bool("True"), "Да")
        self.assertEqual(convert_bool("False"), "Нет")

    def test_convert_bool_reverse(self):
        self.assertEqual(convert_bool_reverse("Да"), True)
        self.assertEqual(convert_bool_reverse("Нет"), False)

    def test_convert_tax(self):
        self.assertEqual(convert_tax("Да"), "Без вычета налогов")
        self.assertEqual(convert_tax("Нет"), "С вычетом налогов")

    def test_fix_salary(self):
        self.assertEqual(fix_salary('1000'), '1 000')
        self.assertEqual(fix_salary('100'), '100')
        self.assertEqual(fix_salary('55000'), '55 000')

    def test_get_date(self):
        self.assertEqual(get_date("2022-07-05T18:22:28+0300"), '05.07.2022')
        self.assertEqual(get_date("2022-07-18T05:14:45+0300"), '18.07.2022')
        self.assertEqual(get_date("2022-12-03T19:16:33+0300"), '03.12.2022')

    def test_line_trim(self):
        long_vac = Vacancy(1, "Системное мышление, Холодные продажи, Деловое общение, Продажа комплексных проектов, "
                              "Тайм-менеджмент, Перевод текстов", "1", 1, 1, 1, 1, 1, 1)
        ans = 'Системное мышление, Холодные продажи, Деловое общение, Продажа комплексных проектов, Тайм-менеджмент...'
        self.assertEqual(line_trim(long_vac, 'description'), ans)

        small_vac = Vacancy(1, "Строка с количеством символов меньше 100", "1", 1, 1, 1, 1, 1, 1)
        ans = "Строка с количеством символов меньше 100"
        self.assertEqual(line_trim(small_vac, 'description'), ans)


class DatasetTest(TestCase):
    def test_init(self):
        data = DataSet("vacancies.csv")
        self.assertEqual(data.file_name, "vacancies.csv")

    def test_csv_reader(self):
        data = DataSet("vacancies.csv")
        self.assertEqual(type(data.csv_reader()[0]).__name__, 'dict')

    def test_csv_filer(self):
        data = DataSet("vacancies.csv")
        self.assertEqual(type(data.csv_filer()[0]).__name__, 'Vacancy')


class VacancyTests(TestCase):
    def test_init(self):
        vacancy = Vacancy("Программист<br>", "Удаленная работа<i>", "Git\nLinux", "between3And6", "True", "Контур",
                          Salary(50000, 80000, "True", "RUR"), "Екатеринбург", "2022-07-05T18:22:28+0300")
        self.assertEqual(vacancy.name, "Программист<br>")
        self.assertEqual(vacancy.description, "Удаленная работа<i>")
        self.assertEqual(vacancy.key_skills, ['Git', 'Linux'])
        self.assertEqual(vacancy.experience_id, "between3And6")
        self.assertEqual(vacancy.premium, "True")
        self.assertEqual(vacancy.employer_name, "Контур")
        self.assertEqual(type(vacancy.salary).__name__, 'Salary')
        self.assertEqual(vacancy.area_name, "Екатеринбург")
        self.assertEqual(vacancy.published_at, "2022-07-05T18:22:28+0300")

    def test_formatter(self):
        vacancy = Vacancy("Программист<br>", "Удаленная работа<i>", "Git\nLinux", "between3And6", "True", "Контур",
                          Salary(50000, 80000, "True", "RUR"), "Екатеринбург", "2022-07-05T18:22:28+0300")
        vacancy.formatter()
        self.assertEqual(vacancy.name, "Программист")
        self.assertEqual(vacancy.description, "Удаленная работа")
        self.assertEqual(vacancy.experience_id, "От 3 до 6 лет")
        self.assertEqual(vacancy.premium, "Да")
        self.assertEqual(vacancy.salary.salary_currency, "Рубли")
        self.assertEqual(vacancy.salary.salary_gross, "Да")


class SalaryTests(TestCase):
    def test_init(self):
        salary = Salary(10000, 30000, "True", "RUR")
        self.assertEqual(type(salary).__name__, 'Salary')
        self.assertEqual(salary.salary_from, 10000)
        self.assertEqual(salary.salary_to, 30000)
        self.assertEqual(salary.salary_gross, 'True')
        self.assertEqual(salary.salary_currency, 'RUR')

    def test_converter(self):
        salary = Salary("10000", "30000", "True", "Тенге")
        self.assertEqual(salary.converter(salary.salary_currency), 2600)
        salary = Salary("10000", "30000", "True", "Рубли")
        self.assertEqual(salary.converter(salary.salary_currency), 20000)
