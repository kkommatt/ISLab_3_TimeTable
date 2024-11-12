import copy
import random

from models.pair import Pair


class TimeTable:
    """
    A class representing a timetable. It holds a grid of time slots with associated group,
    classroom, and lecturer information. This class includes methods for conflict detection,
    timetable validation, crossover between two timetables, and evaluation of various costs
    (e.g., group windows, lector windows, time earliness, and group/classroom capacity).
    """

    def __init__(self):
        self.grid: list[Pair] = []

    def __hash__(self):
        return hash(self.grid)

    def _find_time_conflicts_for_all_groups(self):
        """
        Finds scheduling conflicts for each group. A conflict is identified when a group
        is scheduled at the same time in multiple sessions.

        Returns:
        - dict: A dictionary where keys are group titles, and values are lists of conflicting times.
        """
        times = {}
        for time in self.grid:
            if time.group is None:
                continue
            if time.group.title not in times:
                times[time.group.title] = []
            times[time.group.title].append(time.time)

        conflicts = {}
        for group, time_cases in times.items():
            conflicts[group] = []
            for time in time_cases:
                if time is not None and time_cases.count(time) > 1:
                    conflicts[group].append(time)
        return conflicts

    def _find_time_conflicts_for_all_classrooms(self):
        """
        Finds scheduling conflicts for each classroom. A conflict occurs when a classroom
        is scheduled at the same time for multiple sessions.

        Returns:
        - dict: A dictionary where keys are classroom names, and values are lists of conflicting times.
        """
        times = {}
        for time in self.grid:
            if time.classroom is None:
                continue
            if time.classroom.name not in times:
                times[time.classroom.name] = []
            times[time.classroom.name].append(time.time)

        conflicts = {}
        for classroom, time_cases in times.items():
            conflicts[classroom] = []
            for time in time_cases:
                if time is not None and time_cases.count(time) > 1:
                    conflicts[classroom].append(time)
        return conflicts

    def _find_time_conflicts_for_all_lectors(self):
        """
        Finds scheduling conflicts for each lector. A conflict occurs when a lector
        is scheduled at the same time for multiple sessions.

        Returns:
        - dict: A dictionary where keys are lector names, and values are lists of conflicting times.
        """
        times = {}
        for time in self.grid:
            if time.lector is None:
                continue
            if time.lector.name not in times:
                times[time.lector.name] = []
            times[time.lector.name].append(time.time)

        conflicts = {}
        for lector, time_cases in times.items():
            conflicts[lector] = []
            for time in time_cases:
                if time is not None and time_cases.count(time) > 1:
                    conflicts[lector].append(time)
        return conflicts

    def is_valid(self):
        """
        Checks if the timetable is valid by ensuring there are no conflicts.
        Validity is determined by ensuring that there are no conflicts for groups,
        classrooms, or lectors.

        Returns:
        - tuple: A tuple where:
          - the first element is a boolean indicating whether the timetable is valid (no conflicts),
          - the second, third, and fourth elements are the conflict dictionaries for groups, classrooms,
            and lectors respectively.
        """
        return (
            (
                    not any(self._find_time_conflicts_for_all_groups().values()) and
                    not any(self._find_time_conflicts_for_all_classrooms().values()) and
                    not any(self._find_time_conflicts_for_all_lectors().values())
            ),
            self._find_time_conflicts_for_all_groups(),
            self._find_time_conflicts_for_all_classrooms(),
            self._find_time_conflicts_for_all_lectors(),
        )

    def crossover(self, other):
        """
        Performs a crossover operation between this timetable and another timetable.
        This method generates a new timetable by randomly combining the time slots
        of the two timetables.

        Args:
        - other (TimeTable): The other timetable to crossover with.

        Returns:
        - TimeTable: A new timetable resulting from the crossover.
        """
        timetable = TimeTable()
        timetable.grid = self.grid.copy()

        other_timecases = other.grid
        for i in range(len(self.grid)):
            if random.random() > 0.5:
                timetable.grid[i] = copy.copy(other_timecases[i])

        return timetable

    def __str__(self) -> str:
        """
        Returns a string representation of the timetable.

        Returns:
        - str: A string that represents the timetable, one line per time case.
        """
        return "\n".join([str(time_case) for time_case in self.grid])

    def _get_group_windows_cost(self, time_scores):
        """
        Calculates the cost for group scheduling windows. This is the cost of
        scheduling group sessions with too much time between them.

        Args:
        - time_scores (dict): A dictionary of time scores that indicate the relative
                               'lateness' or 'earliness' of time slots.

        Returns:
        - float: The total cost for group windows.
        """
        times_for_groups = {}
        for time_case in self.grid:
            if time_case.group is None:
                continue
            if time_case.group.title not in times_for_groups:
                times_for_groups[time_case.group.title] = []
            times_for_groups[time_case.group.title].append(time_case.time)

        cost = 0
        for _, v in times_for_groups.items():
            sorted_times = sorted(v, key=lambda x: (x.day, x.time))
            for i in range(len(sorted_times) - 1):
                cost += (time_scores[sorted_times[i + 1]] - time_scores[sorted_times[i]])

        return cost

    def _get_lector_windows_cost(self, time_scores):
        """
        Calculates the cost for lector scheduling windows. Similar to the group windows cost,
        but for lectors.

        Args:
        - time_scores (dict): A dictionary of time scores that indicate the relative
                               'lateness' or 'earliness' of time slots.

        Returns:
        - float: The total cost for lector windows.
        """
        times_for_lectors = {}
        for time_case in self.grid:
            if time_case.lector is None:
                continue
            if time_case.lector.name not in times_for_lectors:
                times_for_lectors[time_case.lector.name] = []
            times_for_lectors[time_case.lector.name].append(time_case.time)

        cost = 0
        for _, v in times_for_lectors.items():
            sorted_times = sorted(v, key=lambda x: (x.day, x.time))
            for i in range(len(sorted_times) - 1):
                cost += (time_scores[sorted_times[i + 1]] - time_scores[sorted_times[i]])

        return cost

    def _get_time_earliness_cost(self, time_scores):
        """
        Calculates the earliness cost for all time slots. The earlier a time slot is, the higher
        the penalty, based on the time score.

        Args:
        - time_scores (dict): A dictionary of time scores for each time slot.

        Returns:
        - float: The total earliness cost across all time slots.
        """
        times = {}
        for time_case in self.grid:
            if time_case.time is None:
                continue
            if time_case.time not in times:
                times[time_case.time] = 0
            times[time_case.time] += 1

        cost = 0
        for k, v in times.items():
            cost += time_scores[k] * v

        return cost

    def _get_group_capacity_classroom_capacity_fill_cost(self):
        """
        Calculates the cost related to the classroom and group capacity. This cost is higher
        when the group size does not fill the classroom to its maximum capacity.

        Returns:
        - float: The cost for group and classroom capacity mismatch.
        """
        cost = 0
        for time_case in self.grid:
            if time_case.classroom is None or time_case.group is None:
                continue
            cost += ((time_case.classroom.max_student_count - time_case.group.student_count) /
                     time_case.classroom.max_student_count)

        return cost


RANDOM_SEED = random.randint(0, 1000)
