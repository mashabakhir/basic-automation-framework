def main():

    annual_salary = float(input("Введите годовую зарплату: "))
    portion_saved = float(input("Введите часть зарплаты для сбережений: "))
    total_cost = float(input("Введите стоимость дома: "))
    semi_annual_raise = float(input("Введите полугодовое повышение зарплаты: "))

    portion_down_payment = 0.25
    investments = 0.04
    current_savings = 0.0
    months = 0

    down_payment = total_cost * portion_down_payment

    while current_savings < down_payment:
        monthly_salary = annual_salary / 12
        current_savings += current_savings * (investments / 12)
        current_savings += monthly_salary * portion_saved
        months += 1

        if months % 6 == 0:
            annual_salary *= (1 + semi_annual_raise)

    print(f"Количество месяцев, необходимых для накопления: {months}")

if __name__ == "__main__":
    main()
