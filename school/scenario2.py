#Сценарій 2

from pathlib import Path

from models import Director, Guard, School, SALARY_COLUMNS, Teacher

DATA_DIR = Path(__file__).parent / "data"
OUTPUT_FILE = Path(__file__).parent / "output" / "salaries.csv"
SCHOOL_NAME = "Ліцей №1"


def main() -> None:
    # та сама школа, що й у сценарії 1: з учнями з CSV та працівниками
    school = School.from_csv(SCHOOL_NAME, DATA_DIR)
    school.employees += [
        Director("Окафор Чіді Емека", 15000, teaching_years=22, management_years=9),
        Teacher("Танака Хіроші Кендзі", 12000, teaching_years=14),
        Teacher("Гарсія Лусія Марія", 12000, teaching_years=8),
        Teacher("Шарма Пріянка Раві", 12000, teaching_years=19),
        Teacher("Аль-Фарсі Юсеф Карім", 12000, teaching_years=11),
        Teacher("Нільсен Астрід Бйорн", 12000, teaching_years=26),
        Teacher("Коваленко Олена Петрівна", 12000, teaching_years=31),
        Teacher("Морган Грейс Девід", 12000, teaching_years=3),
        Guard("Діалло Мусса Ібрагім", 11000, work_years=12),
        Guard("Чжан Вей Цзянь", 11000, work_years=5),
    ]

    print(f"{SCHOOL_NAME}: {school.total_students} учнів, {len(school.employees)} працівників\n")
    name, position, base, salary = SALARY_COLUMNS
    print(f"{name:<28}{position:<12}{base:>15}{salary:>12}")
    for row in school.salary_table():
        print(f"{row[0]:<28}{row[1]:<12}{row[2]:>15,.0f}{row[3]:>12,.2f}")

    school.save_salaries(OUTPUT_FILE)
    print(f"\nТаблицю збережено у {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
