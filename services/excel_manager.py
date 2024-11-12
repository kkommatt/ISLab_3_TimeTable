import json
import random
from collections import defaultdict

import pandas as pd

from services.timetable import RANDOM_SEED
from services.timetable_generator import TimeTableGenerator


def prepare_timetable(data):
    """
    Prepares a timetable from a JSON data structure. This function processes the data,
    groups it by 'group' and 'day', and sorts the days of the week and timeslots for each group.

    Args:
    - data (str): A JSON string representing the raw timetable data.

    Returns:
    - timetable (dict): A nested dictionary with groups as keys, and each group having
                         days of the week as keys, which in turn map to a list of classes
                         scheduled for each day.
    """

    # Parse the input JSON string into Python dictionary
    data = json.loads(data)

    # Use defaultdict to easily append to lists, grouped by 'group' and 'day'
    timetable = defaultdict(lambda: defaultdict(list))

    # Populate the timetable dictionary
    for entry in data:
        group = entry['group']
        day = entry['day']
        time = entry['time']
        subject = entry['subject']
        lector = entry['lector']
        classroom = entry['classroom']

        # Group the data by 'group' and 'day', append the class details
        timetable[group][day].append({
            'time': time,
            'subject': subject,
            'lector': lector,
            'classroom': classroom
        })

    # Sort the days of the week and timeslots within each group
    for group in timetable:
        # Sort days of the week based on the order of weekdays (Monday to Friday)
        timetable[group] = dict(sorted(timetable[group].items(),
                                       key=lambda x: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"].index(
                                           x[0])))

        # For each day, sort the entries by time
        for day in timetable[group]:
            timetable[group][day].sort(key=lambda x: x['time'])

    return timetable


def generate_excel_timetable():
    """
    Generates a timetable in Excel format based on a pre-defined timetable structure.
    This function retrieves the best timetable using a genetic algorithm, processes it,
    and outputs it as an Excel file with the timetable details for each group.

    Returns:
    - None
    """

    # Set the random seed for reproducibility of the timetable generation
    random.seed(RANDOM_SEED)

    # Initialize the timetable manager (presumably a custom class that handles the timetable generation)
    timetable_manager = TimeTableGenerator()

    # Load timetable data from a JSON file
    timetable_manager.from_json("timetable.json")

    # Generate the best timetable using a genetic algorithm with a population of 100
    best_timetable = timetable_manager.genetic(100)

    # Prepare the timetable in a structured format (grouped by day and sorted)
    timetable = prepare_timetable(json.dumps([timetable.to_dict() for timetable in best_timetable.grid]))

    # Prepare data for exporting to Excel
    rows = []

    # Iterate over the timetable and extract relevant details for each row
    for group, days in timetable.items():
        for day, entries in days.items():
            for entry in entries:
                row = {
                    "Group": group,  # Group (e.g., "Math1", "CS2")
                    "Day": day,  # Day of the week (e.g., "Monday")
                    "Time": entry["time"],  # Class start time
                    "Subject": entry["subject"],  # Name of the subject
                    "Lector": entry["lector"],  # Name of the lecturer
                    "Classroom": entry["classroom"]  # Classroom number
                }
                rows.append(row)

    # Convert the rows list into a pandas DataFrame for easier manipulation
    # Set index to ["Day", "Time", "Group"] for better structure in the Excel output
    pd.DataFrame(rows).set_index(["Day", "Time", "Group"]).to_excel("timetable.xlsx")
