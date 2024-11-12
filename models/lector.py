from models.subject import Subject


class Lector:
    """
    Клас, що задає лектора, визначається ім'ям (повним) та предметами, які може викладати лектор

    Attributes:
        name (str): Повне ім'я лектора.
        can_teach (list[str]): Список назв предметів, які може вести цей лектор.
        can_teach_subjects (list[Subject]): Список екземлярів класу Subject, які може вести цей лектор.
    """

    def __init__(self, name: str, can_teach: list[Subject]):
        self.name: str = name
        self.can_teach: list[str] = can_teach
        self.can_teach_subjects: list[Subject] = None

    def __eq__(self, value):
        return (value is not None
                and self.name == value.name)

    def __str__(self):
        return f"{self.name}"

    def __hash__(self):
        return hash(self.name)
