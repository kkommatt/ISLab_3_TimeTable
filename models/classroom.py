class Classroom:
    """Клас, що представляє аудиторію, задається назвою та максимальною кількістю студентів.

        Attributes:
            name (str): Назва аудиторії (e.g., '01', '101').
            max_student_count (int): Максимальна кількість студентів, яка може розміститися в аудиторії.
    """

    def __init__(self, name, max_student_count):
        self.name = name
        self.max_student_count = max_student_count

    def __eq__(self, value):
        return (
                value is not None
                and self.name == value.name
                and self.max_student_count == value.max_student_count
        )

    def __str__(self):
        return f"{self.name}"

    def __hash__(self):
        return hash((self.name, self.max_student_count))
