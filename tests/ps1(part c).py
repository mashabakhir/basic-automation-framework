def main():

    annual_salary = float(input("Введите годовую зарплату: "))

    total_cost = 1000000
    portion_down_payment = 0.25
    investments = 0.04
    semi_annual_raise = 0.07
    months_target = 36
    epsilon = 100

    down_payment = total_cost * portion_down_payment

    def savings_for_36_months(saving_rate):
        current_savings = 0.0
        current_salary = annual_salary
        for month in range(1, months_target + 1):
            current_savings += current_savings * (investments / 12)
            current_savings += (current_salary / 12) * saving_rate
            if month % 6 == 0:
                current_salary *= (1 + semi_annual_raise)
        return current_savings

    if savings_for_36_months(1.0) < down_payment - epsilon:
        print("Невозможно накопить за 36 месяцев.")
        return

    low = 0
    high = 10000
    steps = 0
    best_rate = (high + low) / 2

    while True:
        steps += 1
        saving_rate = best_rate / 10000
        current_savings = savings_for_36_months(saving_rate)

        if abs(current_savings - down_payment) <= epsilon:
            break
        elif current_savings < down_payment:
            low = best_rate
        else:
            high = best_rate

        best_rate = (high + low) / 2

        if high - low < 1:
            break

    print(f"Оптимальная доля сбережений: {saving_rate:.4f}")
    print(f"Количество шагов поиска по бисекции: {steps}")

if __name__ == "__main__":
    main()
