#Сценарій 1

from pathlib import Path

import pandas as pd
import streamlit as st
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from models import LAST_GRADE, Gender, School

DATA_DIR = Path(__file__).parent / "data"
SCHOOL_NAME = "Ліцей №1"


def show_statistics(school: School) -> None:
    shares = school.gender_share()
    largest, smallest = school.largest_class(), school.smallest_class()

    col_total, col_gender, col_average = st.columns(3)
    col_total.metric("Усього учнів", school.total_students)
    col_gender.metric(
        "Хлопці / дівчата",
        f"{shares[Gender.MALE]:.1f}% / {shares[Gender.FEMALE]:.1f}%",
    )
    col_average.metric("Середня кількість учнів у класі", f"{school.average_class_size:.1f}")

    st.write(f"**Найбільший клас:** {largest.name} — {largest.size} учнів")
    st.write(f"**Найменший клас:** {smallest.name} — {smallest.size} учнів")


def new_chart(title: str, xlabel: str, ylabel: str) -> tuple[Figure, Axes]:
    fig = Figure(figsize=(6, 3.8), layout="constrained")
    ax = fig.subplots()
    ax.set(title=title, xlabel=xlabel, ylabel=ylabel)
    ax.grid(alpha=0.3)
    return fig, ax


def show_charts(school: School) -> None:
    classes = pd.DataFrame(
        {
            "name": c.name,
            "grade": c.grade,
            "letter": c.letter,
            "size": c.size,
            "avg_grade": c.average_grade,
        }
        for c in sorted(school.classes, key=lambda c: (c.grade, c.letter))
    )
    left, right = st.columns(2)

    by_grade = classes.groupby("grade")["size"].sum()
    fig, ax = new_chart("Кількість учнів по паралелях", "Паралель", "Учнів")
    ax.bar(by_grade.index.astype(str), by_grade.to_numpy())
    left.pyplot(fig)

    by_letter = classes.groupby("letter")["size"].mean()
    fig, ax = new_chart("Середня кількість учнів по вертикалях", "Вертикаль", "Учнів у класі")
    ax.bar(by_letter.index, by_letter.to_numpy())
    right.pyplot(fig)

    by_birth_year = pd.Series([s.birth_year for s in school.students]).value_counts().sort_index()
    fig, ax = new_chart("Кількість учнів за роком народження", "Рік народження", "Учнів")
    ax.plot(by_birth_year.index, by_birth_year.to_numpy(), marker="o")
    left.pyplot(fig)

    fig, ax = new_chart("Середня оцінка учнів по класах", "Клас", "Середня оцінка")
    ax.scatter(classes["name"], classes["avg_grade"])
    ax.tick_params(axis="x", rotation=90)
    right.pyplot(fig)


def show_checks(before: School, after: School, graduated_count: int) -> None:
    # Перевіряє, що переведення виконано коректно
    # клас N до переведення має стати класом N+1 з тією ж кількістю учнів
    expected = {(c.grade + 1, c.letter): c.size for c in before.classes if c.grade < LAST_GRADE}
    actual = {(c.grade, c.letter): c.size for c in after.classes}

    checks = {
        "Випускні класи зникли зі школи": len(after.classes) == len(before.classes) - graduated_count,
        "Першої паралелі немає": all(c.grade != 1 for c in after.classes),
        "Кожен клас став на паралель старшим з тими самими учнями": expected == actual,
        "Школу залишили лише випускники": (
            before.total_students - after.total_students
            == sum(c.size for c in before.classes if c.grade == LAST_GRADE)
        ),
    }
    for description, passed in checks.items():
        (st.success if passed else st.error)(description)


def main() -> None:
    st.set_page_config(page_title="Статистика школи", layout="wide")
    st.title(f"{SCHOOL_NAME}: статистика по класах")

    school = School.from_csv(SCHOOL_NAME, DATA_DIR)
    promoted = School.from_csv(SCHOOL_NAME, DATA_DIR)
    graduated = promoted.promote_all()

    before_tab, after_tab = st.tabs(["Поточний стан", "Після переведення на рік вперед"])

    with before_tab:
        show_statistics(school)
        show_charts(school)

    with after_tab:
        show_statistics(promoted)
        st.subheader("Перевірка переведення")
        show_checks(school, promoted, len(graduated))

        st.dataframe(
            pd.DataFrame(
                {
                    "Було": c.name,
                    "Стало": f"{c.grade + 1}{c.letter}" if c.grade < LAST_GRADE else "випуск",
                    "Учнів": c.size,
                }
                for c in school.classes
            ),
            hide_index=True,
        )

main()
