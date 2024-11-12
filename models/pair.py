from models.classroom import Classroom
from models.group import Group
from models.lector import Lector
from models.subject import Subject
from models.time import Time


class Pair:
    """
    Клас, що представляє пару, визначається групою, предметом, лектором, аудиторією та часом.

    Attributes:
        group (models.group.Group): Екземляр класу Групи.
        subject (Subject): Екземляр класу Предмет.
        lector (Lector, optional): Екземпляр класу Лектор.
        classroom (Classroom, optional): Екземпляр класу Аудиторії.
        time (Time, optional): Екземляр класу Час.
    """

    def __init__(
            self,
            group: Group,
            subject: Subject,
            lector: Lector = None,
            classroom: Classroom = None,
            time: Time = None,
    ):
        self.group = group
        self.subject = subject
        self.lector = lector
        self.classroom = classroom
        self.time = time

    def __eq__(self, value):
        return (
                self.group == value.group
                and self.subject == value.subject
                and self.lector == value.lector
                and self.classroom == value.classroom
                and self.time == value.time
        )

    def __str__(self) -> str:
        return f"Group: {self.group.title}, Subject: {self.subject.name}, Lector: {self.lector}, Classroom: {self.classroom}, Time: {self.time}"

    def __repr__(self) -> str:
        return f"Group: {self.group.title}, Subject: {self.subject.name}, Lector: {self.lector}, Classroom: {self.classroom}, Time: {self.time}"

    def __hash__(self) -> int:
        return hash(
            (self.group, self.subject, self.lector, self.classroom, self.time)
        )

    def to_table_format(self):
        return f"Day - {self.time.day}\nNumber - {self.time.time}\n Group - {self.group.title}\nSubject - {self.subject.name}\nLector - {self.lector.name}\nClassroom - {self.classroom.name}"

    def to_dict(self):
        return {
            'group': self.group.title,
            'subject': self.subject.name,
            'lector': self.lector.name,
            'classroom': self.classroom.name,
            'day': self.time.day,
            'time': self.time.time
        }
