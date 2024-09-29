import sqlite3
from datetime import datetime
import smtplib
import qrcode


def ConnectDb():
    try:
        sqliteConnection = sqlite3.connect("db.sqlite3")
        cursor = sqliteConnection.cursor()
        return cursor
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)


def PrintHomeScreen():
    print(
        '''Welcome to Train Ticket Booking System
1) Purchase Ticket
2) Add Schedule
0) Exit 
'''
    )


def HomeScreen():
    PrintHomeScreen()
    option = input("Please select an option: ")

    while option != '0':
        if option == '1':
            SelectTrip()
            option = None
        elif option == '2':
            user = input("Please enter username: ")
            password = input("Please enter password: ")
            if user == "admin" and password == "password":
                AdminHomeScreem()
                option = None
            else:
                print("Invalid username or password")
                option = None
        else:
            PrintHomeScreen()
            option = input("Please select an option: ")
    return


def AdminHomeScreem():
    print('1) Add schedule\n0)Back')
    option = input("Please select an option: ")
    while option != '0':
        if option == '1':
            AddSchedule()
            option = None
        else:
            print('1) Add schedule\n0)Back')
            option = input("Please select an option: ")


def AddSchedule():
    origin = input("Please enter origin name: ")
    while len(origin.strip()) == 0:
        print("Please enter a valid origin name")
        origin = input("Please enter origin name: ")
    destination = input("Please enter destination name: ")
    while len(destination.strip()) == 0:
        print("Please enter a valid origin name")
        destination = input("Please enter origin name: ")
    departure_datetime = input("Please enter departure date and time (yyyy-mm-dd hh:mm) : ")
    valid = False
    while not valid:
        try:
            datetime.strptime(departure_datetime, "%Y-%m-%d %H:%M")
            valid = True
        except ValueError:
            departure_datetime = input("Please enter a valid departure date and time (yyyy-mm-dd hh:mm) : ")

    return_datetime = input("Please enter return date and time (yyyy-mm-dd hh:mm): ")
    valid = False
    while not valid:
        try:
            datetime.strptime(return_datetime, "%Y-%m-%d %H:%M")
            valid = True
        except ValueError:
            return_datetime = input("Please enter a valid departure date and time (yyyy-mm-dd hh:mm) : ")

    cursor = ConnectDb()
    sql_query = (f"INSERT INTO train_info (origin, destination, departure_datetime, return_datetime, full) "
                 f"VALUES ('{origin}', '{destination}', '{departure_datetime}', '{return_datetime}', 0); ")

    cursor.execute(sql_query)
    trip_id = cursor.lastrowid

    for i in range(1, 7):
        sql_query = (f"INSERT INTO coach (coach_num, full, trip_id) "
                     f"VALUES ")
        sql_query = sql_query + f"({i}, 0, {trip_id});"
        cursor.execute(sql_query)

        sql_query = f"INSERT INTO seat (seat_num, coach_id, status) VALUES "

        for x in range(1, 21):
            sql_query = sql_query + f"({x}, {cursor.lastrowid}, 'A')"
            if x == 20:
                sql_query = sql_query + ";"
            else:
                sql_query = sql_query + ", "

        cursor.execute(sql_query)
    cursor.connection.commit()


def SelectTrip():
    origin = input("Select an origin: ")
    destination = input("Select a destinaion: ")
    departure_date = input("Enter departure date (yyyy-mm-dd): ")
    return_date = input("Enter return date (yyyy-mm-dd): ")

    cursor = ConnectDb()
    sql_query = (f'SELECT *, case when full = 1 then "X" else "O" end as status '
                 f'FROM train_info WHERE origin = "{origin}" AND destination = "{destination}" AND '
                 f'date(departure_datetime) = "{departure_date}" AND date(return_datetime) = "{return_date}"')

    cursor.execute(sql_query)
    col_name = [d[0] for d in cursor.description]
    data = [dict(zip(col_name, r)) for r in cursor.fetchall()]

    if len(data) == 0:
        print("There is no train available for this trip\n")
        return

    print(f"{'ID':<5}{'Origin':<20}{'Destination':<20}{'Departure Date':<25}{'Return Date':<25}{'Full'}")
    for row in data:
        print(f"{row['Id']:<5}{row['origin']:<20}{row['destination']:<20}{row['departure_datetime']:<25}"
              f"{row['return_datetime']:<25}{row['status']:<5}")
    trip_id = input("Enter trip ID: ")
    TrainBooking(trip_id)


def TrainBooking(trip_id):
    cursor = ConnectDb()
    sql_query = f'SELECT full FROM train_info WHERE ID = {trip_id}'
    cursor.execute(sql_query)
    row = cursor.fetchone()
    if row[0] == '0':
        print("The seats are all sold out for this train")
        return
    SelectCoach(trip_id)


def SelectCoach(trip_id):
    cursor = ConnectDb()
    sql_query = f'SELECT * FROM coach where trip_id = {trip_id} and full = 0'
    cursor.execute(sql_query)
    col_name = [d[0] for d in cursor.description]
    data = [dict(zip(col_name, r)) for r in cursor.fetchall()]

    if len(data) == 0:
        print("The seats are all sold out for this train")
        return

    # Nid to loop back if user didn't enter a valid coach number
    available_coach = []
    print('Available coaches:')
    for row in data:
        print(f'Coach - {row["coach_num"]}')
        available_coach.append(row["coach_num"])
    coach_num = input("Please select a coach number: ")

    if int(coach_num) not in available_coach:
        print("The coach number is not available")
    else:
        coach_id = [d for d in data if d['coach_num'] == int(coach_num)]
        SelectSeat(trip_id, coach_id[0]['Id'])


def SelectSeat(trip_id, coach_id):
    cursor = ConnectDb()
    sql_query = (f'SELECT a.*, b.trip_id, b.coach_num FROM seat a inner join coach b on a.coach_id = b.Id '
                 f'where b.trip_id = {trip_id} and a.coach_id = {coach_id} and status = "A"')
    cursor.execute(sql_query)
    col_name = [d[0] for d in cursor.description]
    datas = [dict(zip(col_name, r)) for r in cursor.fetchall()]
    available_seats = []
    print("Available seats:")
    print(f"{'coach':<15}{'seat':<10}")
    for data in datas:
        print(f'{data["coach_num"]:<10}{data["seat_num"]:<10}')
        available_seats.append(data["seat_num"])
    selected_seat = input("Please select a seat: ")
    while int(selected_seat) not in available_seats and int(selected_seat) != 0:
        selected_seat = input("The seat is not available. Please select a valid seat or press 0 to go back home page: ")

    if int(selected_seat) == 0:
        return
    else:
        sql_query = (f"UPDATE seat "
                     f"SET status = 'R' "
                     f"WHERE id = {selected_seat};")
        cursor.execute(sql_query)

        cursor.connection.commit()

        DisplaySelectedSeatDetails(selected_seat, coach_id)


def DisplaySelectedSeatDetails(selected_seat, coach_id):
    cursor = ConnectDb()
    sql_query = (f'SELECT a.seat_num, a.coach_id, b.coach_num, c.* FROM seat a '
                 f'inner join coach b on a.coach_id = b.id '
                 f'inner join train_info c on b.trip_id = c.Id '
                 f'where a.seat_num = {selected_seat} AND a.coach_id = {coach_id}')
    cursor.execute(sql_query)
    col_name = [d[0] for d in cursor.description]
    datas = [dict(zip(col_name, r)) for r in cursor.fetchall()]
    print(sql_query)
    print('Below are the trip details:')
    print(f"From: {datas[0]['origin']}")
    print(f"To: {datas[0]['destination']}")
    print(f"Departure Date: {datas[0]['departure_datetime']}")
    print(f"Return Date: {datas[0]['return_datetime']}")
    print(f"Coach: {datas[0]['coach_num']}")
    print(f"Seat: {datas[0]['seat_num']}")

    confirm = input("Confirm seat? (y/n): ")

    if confirm == 'y':
        ConfirmBooking(selected_seat, coach_id)
        CreateQRCode(datas)
        print('QR code created')
    elif confirm == 'n':
        sql_query = (f"UPDATE seat "
                     f"SET status = 'A' "
                     f"WHERE id = {selected_seat};")
        cursor.execute(sql_query)

        cursor.connection.commit()
        SelectSeat(datas[0]['Id'], datas[0]['coach_id'])


def ConfirmBooking(selected_seat, coach_id):
    cursor = ConnectDb()

    sql_query = (f"UPDATE seat "
                 f"SET status = 'X' "
                 f"WHERE seat_num = {selected_seat} AND coach_id = {coach_id};")
    cursor.execute(sql_query)

    cursor.connection.commit()
    email = input("Enter email: ")
    print(f"An email will be sent to {email} shortly")


def SendEmail(email):
    pass


def CreateQRCode(data):
    print(data)
    img = qrcode.make(data)
    img.save('qrcode.png')


def main():
    HomeScreen()
    # AddSchedule()


if __name__ == '__main__':
    main()
