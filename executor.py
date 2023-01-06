import diagrams
import statistic

value = input()
if value == "Кансии":
    statistic.execute()
elif value == "Статистика":
    diagrams.execute()
else:
    print("Некорректный ввод")
