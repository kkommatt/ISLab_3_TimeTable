import copy
import json
import random

from models.classroom import Classroom
from models.group import Group
from models.lector import Lector
from models.pair import Pair
from models.subject import Subject
from models.time import Time
from services.timetable import TimeTable


class TimeTableGenerator:
    """
    A class responsible for generating and optimizing timetables using a genetic algorithm.
    This class handles data loading, timetable initialization, mutation, crossover,
    and fitness evaluation. It also contains methods for selecting the best timetables
    based on multiple optimization criteria.
    """

    def __init__(self):
        """
        Initializes the timetable generator with empty data structures.

        Attributes:
        - times (list[Time]): List of time slots.
        - subjects (list[Subject]): List of subjects that can be taught.
        - groups (list[Group]): List of student groups.
        - lectors (list[Lector]): List of available lectors.
        - classrooms (list[Classroom]): List of available classrooms.
        - time_scores (dict): A dictionary mapping time slots to their 'lateness' or 'earliness' score.
        - group_windows_weight (float): Weight for the group windows cost.
        - lector_windows_weight (float): Weight for the lector windows cost.
        - time_earliness_weight (float): Weight for the time earliness cost.
        - group_capacity_classroom_capacity_fill_weight (float): Weight for the group/classroom capacity fill cost.
        """
        self.times: list[Time] = None
        self.subjects: list[Subject] = None
        self.groups: list[Group] = None
        self.lectors: list[Lector] = None
        self.classrooms: list[Classroom] = None
        self.time_scores: dict[str, int] = {}

        # Weights for different fitness components
        self.group_windows_weight = 1
        self.lector_windows_weight = 1
        self.time_earliness_weight = 0.5
        self.group_capacity_classroom_capacity_fill_weight = 0.5

    def from_json(self, file_path: str):
        """
        Loads timetable data from a JSON file. This method reads the times, subjects, groups,
        lectors, and classrooms data from the file and initializes the corresponding class attributes.

        Args:
        - file_path (str): The file path to the JSON file containing timetable data.
        """
        with open(file_path, "r") as file:
            data = json.load(file)

            # Load times, subjects, groups, lectors, classrooms from the JSON data
            self.times = [Time(**times) for times in data["times"]]
            self.subjects = [Subject(**subject) for subject in data["subjects"]]
            self.groups = [Group(**group) for group in data["groups"]]
            self.lectors = [Lector(**lector) for lector in data["lectors"]]
            self.classrooms = [Classroom(**classroom) for classroom in data["classrooms"]]

        # Assign a time score based on the index in the list
        for i, times in enumerate(self.times):
            self.time_scores[times] = i

    def create_empty_timetable(self):
        """
        Creates an empty timetable by assigning each group to its subjects based on the hours required
        for each subject. Initially, no times, classrooms, or lectors are assigned.

        Returns:
        - TimeTable: A newly created empty timetable with subjects assigned to the appropriate groups.
        """
        timetable = TimeTable()
        for group in self.groups:
            for subject in group.subject_names:
                s = next((s for s in self.subjects if s.name == subject), None)
                for i in range(s.hours):
                    timetable.grid.append(
                        Pair(
                            group=group,
                            subject=s,
                        )
                    )

        return timetable

    def _get_available_time_for_classroom_and_lector_and_group(
            self, timetable: TimeTable, classroom: Classroom, lector: Lector, group: Group
    ):
        """
        Retrieves the available time slots for a given classroom, lector, and group, taking into account
        the already scheduled sessions in the timetable.

        Args:
        - timetable (TimeTable): The current timetable.
        - classroom (Classroom): The classroom in question.
        - lector (Lector): The lector in question.
        - group (Group): The group in question.

        Returns:
        - list[Time]: A list of available time slots, sorted by day and time.
        """
        grid = timetable.grid
        allowed_times = [ts for ts in self.times]
        busy_times = []
        for s in grid:
            if s.classroom == classroom:
                busy_times.append(s.time)
            if s.lector == lector:
                busy_times.append(s.time)
            if s.group == group:
                busy_times.append(s.time)

        return sorted(
            list(set(allowed_times) - set(busy_times)),
            key=lambda x: (x.day, x.time),
        )

    def _get_available_lectors_for_time_and_subject(
            self, timetable: TimeTable, times: Time, subject: Subject
    ):
        """
        Retrieves the available lectors for a given time slot and subject, ensuring that the lector
        can teach the subject and is not already assigned to another class at that time.

        Args:
        - timetable (TimeTable): The current timetable.
        - times (Time): The time slot in question.
        - subject (Subject): The subject to be taught.

        Returns:
        - list[Lector]: A list of available lectors, sorted by name.
        """
        if times is None:
            return []

        grid = timetable.grid
        allowed_lectors = [l for l in self.lectors if subject.name in l.can_teach]
        busy_lectors = []
        for s in grid:
            if s.time == times:
                busy_lectors.append(s.lector)

        return sorted(
            list(set(allowed_lectors) - set(busy_lectors)), key=lambda x: x.name
        )

    def _get_available_classroom_for_time_and_group(
            self, timetable: TimeTable, times: Time, group: Group
    ):
        """
        Retrieves the available classrooms for a given time slot and group, ensuring that the group
        fits within the classroom's maximum student capacity and the classroom is not already booked.

        Args:
        - timetable (TimeTable): The current timetable.
        - times (Time): The time slot in question.
        - group (Group): The group in question.

        Returns:
        - list[Classroom]: A list of available classrooms, sorted by name.
        """
        grid = timetable.grid
        busy_classrooms = []
        allowed_classrooms = [h for h in self.classrooms if group.student_count <= h.max_student_count]
        for s in grid:
            if s.time == times:
                busy_classrooms.append(s.classroom)

        return sorted(list(set(allowed_classrooms) - set(busy_classrooms)), key=lambda x: x.name)

    def mutate_timetable(self, timetable: TimeTable):
        """
        Mutates a given timetable by randomly altering one of the time slots. The mutation can
        involve changing the classroom, lector, or time of a randomly selected time slot.

        Args:
        - timetable (TimeTable): The current timetable to be mutated.

        Returns:
        - tuple: A tuple containing the mutated timetable and a boolean indicating whether a mutation occurred.
        """
        grid = timetable.grid
        time_index = random.randint(0, len(grid) - 1)
        time_case = grid[time_index]
        new_time_case = copy.copy(time_case)
        what_to_mutate = random.choice(["classroom", "lector", "time"])

        if what_to_mutate == "classroom":
            available_classroom = self._get_available_classroom_for_time_and_group(
                timetable, time_case.time, time_case.group
            )
            if len(available_classroom) == 0:
                return timetable, False
            new_time_case.classroom = random.choice(available_classroom)
            did_mutate = True
        elif what_to_mutate == "lector":
            available_lectors = (
                self._get_available_lectors_for_time_and_subject(
                    timetable, time_case.time, time_case.subject
                )
            )
            if len(available_lectors) == 0:
                return timetable, False
            new_time_case.lector = random.choice(available_lectors)
            did_mutate = True
        else:
            avaliable_time_cases = (
                self._get_available_time_for_classroom_and_lector_and_group(
                    timetable, time_case.classroom, time_case.lector, time_case.group
                )
            )
            if len(avaliable_time_cases) == 0:
                return timetable, False
            new_time_case.time = random.choice(avaliable_time_cases)
            did_mutate = True

        # Create a new timetable with the mutated time case
        new_timetable = copy.copy(timetable)
        new_timetable.grid[time_index] = new_time_case

        return new_timetable, did_mutate

    def init_random_timetable(self):
        """
        Initializes a random timetable by first creating an empty timetable and then
        performing random mutations until the timetable is fully populated with valid
        classrooms, lectors, and times.

        Returns:
        - TimeTable: A randomly initialized timetable.
        """
        timetable = self.create_empty_timetable()

        i = 0
        while i < 1000:
            timetable, _ = self.mutate_timetable(timetable)
            i += 1

        # Fill in None values (classrooms, lectors, times) randomly
        for time_case in timetable.grid:
            if time_case.classroom is None:
                available_classrooms = self._get_available_classroom_for_time_and_group(
                    timetable, time_case.time, time_case.group
                )
                if len(available_classrooms) == 0:
                    return self.init_random_timetable()
                time_case.classroom = random.choice(available_classrooms)

            if time_case.lector is None:
                available_lectors = (
                    self._get_available_lectors_for_time_and_subject(
                        timetable, time_case.time, time_case.subject
                    )
                )
                if len(available_lectors) == 0:
                    return self.init_random_timetable()
                time_case.lector = random.choice(available_lectors)

            if time_case.time is None:
                avaliable_times = (
                    self._get_available_time_for_classroom_and_lector_and_group(
                        timetable, time_case.classroom, time_case.lector, time_case.group
                    )
                )
                if len(avaliable_times) == 0:
                    return self.init_random_timetable()
                time_case.time = random.choice(avaliable_times)

        return timetable

    def get_timetable_fitness(self, timetable: TimeTable):
        """
        Calculates the fitness of a timetable by evaluating various cost components. The
        fitness score is based on the inverse of the total cost.

        Args:
        - timetable (TimeTable): The timetable to be evaluated.

        Returns:
        - float: The fitness score of the timetable (higher is better).
        """
        cost = 0

        # Calculate costs based on various constraints
        group_windows_cost = (
                self.group_windows_weight
                * timetable._get_group_windows_cost(self.time_scores)
        )
        lector_windows_cost = (
                self.lector_windows_weight
                * timetable._get_lector_windows_cost(self.time_scores)
        )
        time_earliness_cost = (
                self.time_earliness_weight
                * timetable._get_time_earliness_cost(self.time_scores)
        )
        group_capacity_classroom_capacity_fill_cost = (
                self.group_capacity_classroom_capacity_fill_weight
                * timetable._get_group_capacity_classroom_capacity_fill_cost()
        )

        # Total cost (sum of all individual costs)
        cost += (
                group_windows_cost
                + lector_windows_cost
                + time_earliness_cost
                + group_capacity_classroom_capacity_fill_cost
        )

        # Fitness is the inverse of the total cost
        return 1 / (1 + cost)

    def tournament_selection(self, population, tournament_size) -> TimeTable:
        """
        Selects the best timetable from a random subset (tournament) of the population.

        Args:
        - population (list[TimeTable]): The current population of timetables.
        - tournament_size (int): The number of timetables to randomly select for the tournament.

        Returns:
        - TimeTable: The best timetable from the selected subset.
        """
        selected = []
        for _ in range(tournament_size):
            selected.append(random.choice(population))

        return max(selected, key=lambda x: self.get_timetable_fitness(x))

    def genetic(self, population_size: int) -> TimeTable:
        """
        Runs a genetic algorithm to optimize timetables. This method evolves a population of
        timetables through selection, crossover, mutation, and fitness evaluation.

        Args:
        - population_size (int): The size of the population for the genetic algorithm.

        Returns:
        - TimeTable: The best timetable found after running the genetic algorithm.
        """
        current_population = []
        for _ in range(population_size):
            current_population.append(self.init_random_timetable())

        number_of_same_best_fitness = 0
        curr_best_fitness = 0
        number_of_generations = 100

        while number_of_generations > 0 and number_of_same_best_fitness < 10:
            new_population = []
            while len(new_population) < population_size:
                parent1 = self.tournament_selection(current_population, 10)
                parent2 = self.tournament_selection(current_population, 10)
                child = parent1.crossover(parent2)
                if random.random() < 0.5:
                    child, _ = self.mutate_timetable(child)
                if child.is_valid()[0]:
                    new_population.append(child)

            current_population = new_population
            best_fitness = self.get_timetable_fitness(
                max(current_population, key=lambda x: self.get_timetable_fitness(x))
            )
            if best_fitness > curr_best_fitness:
                curr_best_fitness = best_fitness
                number_of_same_best_fitness = 0
            elif best_fitness == curr_best_fitness:
                number_of_same_best_fitness += 1

        best_timetable = max(
            current_population, key=lambda x: self.get_timetable_fitness(x)
        )

        return best_timetable
