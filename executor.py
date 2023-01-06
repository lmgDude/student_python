import diagrams
import statistic

value = input()
if value == "Аакансии":
    statistic.execute()
elif value == "Статистика":
    diagrams.execute()
else:
    print("Некорректный ввод")
