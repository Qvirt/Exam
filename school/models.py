#Спільні сутності школи, які використовуються в обох сценаріях

import csv
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from statistics import fmean
from typing import ClassVar, Self

FIRST_GRADE = 1
LAST_GRADE = 11
MAX_MARK = 12

SALARY_COLUMNS = ("ПІБ", "Посада", "Базова ставка", "Зарплата")


class Gender(str, Enum):
    MALE = "Ч"
    FEMALE = "Ж"


@dataclass
class Student:
    last_name: str
    first_name: str
    patronymic: str
    birth_year: int
    gender: Gender
    avg_grade: float

    def __post_init__(self) -> None:
        if not 1 <= self.avg_grade <= MAX_MARK:
            raise ValueError(f"Середня оцінка поза межами 1–{MAX_MARK}: {self.full_name}")

    @property
    def full_name(self) -> str:
        return f"{self.last_name} {self.first_name} {self.patronymic}"


@dataclass
class SchoolClass:
    grade: int
    letter: str
    students: list[Student] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not FIRST_GRADE <= self.grade <= LAST_GRADE:
            raise ValueError(f"Паралель має бути від {FIRST_GRADE} до {LAST_GRADE}, отримано {self.grade}")

    @property
    def name(self) -> str:
        return f"{self.grade}{self.letter}"

    @property
    def size(self) -> int:
        return len(self.students)

    @property
    def average_grade(self) -> float:
        return fmean(s.avg_grade for s in self.students) if self.students else 0.0

    def promote(self) -> None:
        #Переводить клас у наступну паралель, учні залишаються ті самі
        if self.grade == LAST_GRADE:
            raise ValueError(f"{self.name} — випускний клас, його не можна перевести далі")
        self.grade += 1


@dataclass
class Employee(ABC):
    full_name: str
    base_salary: float

    position: ClassVar[str]

    @abstractmethod
    def calculate_salary(self) -> float:
        #Розраховує зарплату за формулою відповідної посади
        pass

@dataclass
class Director(Employee):
    teaching_years: int
    management_years: int

    position: ClassVar[str] = "Директор"

    def calculate_salary(self) -> float:
        return self.base_salary * self.teaching_years / 50 + self.management_years * 500


@dataclass
class Teacher(Employee):
    teaching_years: int

    position: ClassVar[str] = "Вчитель"

    def calculate_salary(self) -> float:
        return self.base_salary * self.teaching_years / 30


@dataclass
class Guard(Employee):
    work_years: int

    position: ClassVar[str] = "Охоронець"

    def calculate_salary(self) -> float:
        return self.base_salary + self.work_years * 250


@dataclass
class School:
    name: str
    classes: list[SchoolClass] = field(default_factory=list)
    employees: list[Employee] = field(default_factory=list)

    @classmethod
    def from_csv(cls, name: str, data_dir: Path) -> Self:
        #Читає classes.csv та students.csv з вказаної теки
        school = cls(name)
        by_key: dict[tuple[int, str], SchoolClass] = {}

        with open(data_dir / "classes.csv", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                school_class = SchoolClass(int(row["grade"]), row["letter"])
                by_key[school_class.grade, school_class.letter] = school_class
                school.classes.append(school_class)

        with open(data_dir / "students.csv", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                key = int(row["grade"]), row["letter"]
                student = Student(
                    last_name=row["last_name"],
                    first_name=row["first_name"],
                    patronymic=row["patronymic"],
                    birth_year=int(row["birth_year"]),
                    gender=Gender(row["gender"]),
                    avg_grade=float(row["avg_grade"]),
                )
                if key not in by_key:
                    raise ValueError(f"Учень {student.full_name} належить до невідомого класу {key[0]}{key[1]}")
                by_key[key].students.append(student)

        return school

    @property
    def students(self) -> list[Student]:
        return [student for school_class in self.classes for student in school_class.students]

    @property
    def total_students(self) -> int:
        return sum(school_class.size for school_class in self.classes)

    @property
    def average_class_size(self) -> float:
        return fmean(c.size for c in self.classes) if self.classes else 0.0

    def gender_share(self) -> dict[Gender, float]:
        #Частка кожної статі серед учнів у відсотках
        students = self.students
        total = max(len(students), 1)
        return {g: 100 * sum(s.gender is g for s in students) / total for g in Gender}

    def largest_class(self) -> SchoolClass:
        return max(self.classes, key=lambda c: c.size)

    def smallest_class(self) -> SchoolClass:
        return min(self.classes, key=lambda c: c.size)

    def promote_all(self) -> list[SchoolClass]:
        #Переводить усі класи на рік вперед. Повертає випускні класи, які залишили школу
        graduated = [c for c in self.classes if c.grade == LAST_GRADE]
        self.classes = [c for c in self.classes if c.grade != LAST_GRADE]
        for school_class in self.classes:
            school_class.promote()
        return graduated

    def salary_table(self) -> list[tuple[str, str, float, float]]:
        return [
            (e.full_name, e.position, e.base_salary, round(e.calculate_salary(), 2))
            for e in self.employees
        ]

    def save_salaries(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        # utf-8-sig, щоб Excel коректно відкривав кирилицю
        with open(path, "w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(SALARY_COLUMNS)
            writer.writerows(self.salary_table())
