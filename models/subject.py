class Subject:
    """
        Клас, що визначає предмет, задається назвою та кількістю годин

        Attributes:
            name (str): Назва предмета (e.g., 'OOP', 'Math Analysis').
            hours (int): Кількість годин для предмету.
    """

    def __init__(self, name, hours):
        self.name: str = name
        self.hours: int = hours

    def __eq__(self, value):
        return (
                value is not None
                and self.name == value.name
                and self.hours == value.hours
        )

    def __str__(self):
        return f"{self.name}"

    def __hash__(self):
        return hash((self.name, self.hours))
