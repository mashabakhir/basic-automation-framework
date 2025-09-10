import math

def main():
    try:

        x = float(input("Введите число x: "))

        y = float(input("Введите число y: "))
    except ValueError:
        print("Вводить ноль нельзя!")
        return

    power = x ** y
    print(f"{x} в степени {y} = {power}")

    if x > 0:
        log2 = math.log2(x)
        print(f"Логарифм числа {x} по основанию 2 = {log2}")
    else:
        print("Число должно быть больше 0, иначе мы не сможем посчитать логарифм.")

if __name__ == "__main__":
    main()
