# ISLab_3_TimeTable

The first step is to upload input data such as available time slots, subjects, student groups, teachers, and classrooms. The data is converted into Python objects, which forms the basis for scheduling.

Next, an empty schedule is created in which subjects are assigned to groups based on the number of hours. This step provides the basic structure of the schedule.

After that, classrooms, teachers, and times are randomly assigned for each subject, group, and time slot. This is done using random mutations to ensure that each item is assigned a classroom, teacher, and time.

The fitness function is used to evaluate the schedule in terms of various constraints and goals, such as avoiding large gaps between sessions for groups and lecturers, early or late load, and proper utilization of classrooms.

After the schedule is evaluated using the fitness function, it is optimized using a genetic algorithm. A population of schedules is created and evaluated for suitability. The best options are selected, which then proceed to crossover and mutation to create new schedules and feasibility. The process is repeated several times to optimize the schedule.

Once the schedule validation is complete, the best schedule is exported to an Excel file that automatically opens for viewing using a spreadsheet program.
