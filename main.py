import os

from services.excel_manager import generate_excel_timetable

if __name__ == "__main__":
    print("TimeTable is generating . . .")
    try:
        generate_excel_timetable()
        print("TimeTable in file 'timetable.xlsx'")
        os.startfile('timetable.xlsx')
    except Exception as e:
        print(e)
