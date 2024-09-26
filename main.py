import sqlite3

def ConnectDb():
    try:
        sqliteConnection = sqlite3.connect("db.sqlite3")
        cursor = sqliteConnection.cursor()
        print("Database created and Successfully Connected to SQLite")

        sqlite_select_Query = "select sqlite_version();"
        cursor.execute(sqlite_select_Query)
        record = cursor.fetchall()
        print("SQLite Database Version is: ", record)
        cursor.close()

    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")


def HomeScreen():
    print(
        '''Welcome to Train Ticket Booking System
1) Purchase Ticket
0) Exit 
'''
    )
    option = input("Please select an option: ")

    while(option != '0'):
        if option == '1':
            option = None
        else:
            option = input("Enter 1 to continue, 0 to exit")
    return

def SelectTrip():
    origin = input("Select an origin: ")
    destination = input("Select a destinaion: ")
    departure_date = input("Enter departure date (yyyy-mm-dd): ")
    return_date = input("Enter return date (yyyy-mm-dd): ")


def main():
    ConnectDb()
    HomeScreen()

if __name__ == '__main__':
    main()
