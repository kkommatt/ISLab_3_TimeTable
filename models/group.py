from models.subject import Subject


class Group:
    """
        Клас, що визначає групу, задається назвою, кількістю студентів та предметами.

        Attributes:
            title (str): Назва групи (e.g., 'K-17', 'TTP-42').
            student_count (int): Кількість студентів в групі.
            subject_names (list[str]): Список назв предметів, які проходить група.
            subjects (list[models.subject.Subject]): Список екземлярів класу Subject, які проходить група.
        """

    def __init__(self, title, student_count, subject_names):
        self.title: str = title
        self.student_count: int = student_count
        self.subject_names: list[str] = [subject_name for subject_name in subject_names]
        self.subjects: list[Subject] = None

    def __eq__(self, value):
        return (
                value is not None
                and self.title == value.title
                and self.student_count == value.student_count
        )

    def __str__(self):
        return f"{self.title}"

    def __hash__(self):
        return hash((self.title, self.student_count))
