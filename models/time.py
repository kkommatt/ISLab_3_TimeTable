class Time:
    """
    Клас, що визначає час, задається днем та номером пари.

    Attributes:
        day (str): День робочого тижня (e.g., 'Monday', 'Tuesday').
        time (str): Номер пари, за умовою не може бути більше 4 (e.g., '1', '2').
    """

    def __init__(self, day: str, time: str):
        self.day: str = day
        self.time: str = time
    def __eq__(self, value):
        return (value is not None
                and self.day == value.day
                and self.time == value.time)

    def __str__(self):
        return f"{self.day}, {self.time}"

    def __repr__(self):
        return f"{self.day}, {self.time}"

    def __hash__(self):
        return hash((self.day, self.time))
