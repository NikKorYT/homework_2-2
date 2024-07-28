from collections import UserDict
import datetime
import pickle
from abc import ABC, abstractmethod


def input_error(func):
    def inner(*args, **kwargs):

        try:
            return func(*args, **kwargs)

        except ValueError:
            return "Please try again and add all nessesary arguments, or delete extra arguments."

        except KeyError:
            return "Invalid contact name. Please try again."

        except IndexError:
            return "Contact not found."

    return inner


class Field:
    def __init__(self, value: str):
        self.value = value

    # return the value of the field as a string
    def __str__(self):
        return str(self.value)


class Name(Field):
    # реалізація класу
    pass


class Phone(Field):
    def __init__(self, value: str):
        super().__init__(value)

        # check if the phone number contains 10 digits
        if not value.isdigit() or len(value) != 10:
            raise ValueError(
                "Invalid phone number. It must be 10 digits. Please try again."
            )


class Birthday(Field):
    def __init__(self, value: str):
        try:
            # Додайте перевірку коректності даних
            # та перетворіть рядок на об'єкт datetime
            self.value = datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError


class Record:
    def __init__(self, name: str):
        self.name = name
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if not isinstance(phone, Phone):
            phone = Phone(phone)
        self.phones.append(phone)

    def remove_phone(self, phone):
        self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        phone_values = [phone.value for phone in self.phones]
        self.phones[phone_values.index(old_phone.value)] = new_phone

    def find_phone(self, phone):
        phone_obj = Phone(phone)
        return self.phones[self.phones.index(phone_obj)]

    def add_birthday(self, birthday: str):
        try:
            self.birthday = Birthday(birthday)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY. Please try again.")

    def show_birthday(self, name):
        print(f"{name}'s birthday is {self.birthday.value}")

    def birthdays(self, name):
        AddressBook.birthdays(name)

    def __str__(self) -> str:
        return f"Contact name: {self.name}, phones: {'; '.join(str(p) for p in self.phones)}, birthday: {self.birthday.value if self.birthday else '-'}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name] = record

    def find(self, name) -> Record:
        try:
            return self.data[name]
        except KeyError:
            return None

    def delete(self, name):
        del self.data[name]

    def birthdays(self) -> list:
        """Function to get upcoming birthdays within 7 days from given list of dictionaries
        and return a list of dictionaries with name and congratulation date
        Congratulation date is set to the next working day if birthday is on Saturday or Sunday
        """
        users = self.data
        upcoming_birthdays = []  # return list

        for user in users:
            record = users[user]
            bday_user = {}  # dictionary for each iteration
            birthday = datetime.datetime.strptime(
                users[user].birthday.value.strftime("%Y.%m.%d"), "%Y.%m.%d"
            ).date()  # convert string to date

            today = datetime.date.today()  # get today's date

            if (
                birthday.replace(year=today.year) < today
            ):  # check if birthday has already passed
                bday_this_year = birthday.replace(
                    year=today.year + 1
                )  # if yes, set next year's birthday
            else:
                bday_this_year = birthday.replace(
                    year=today.year
                )  # if no, set this year's birthday

            # check if birthday is 29 February and this year is not a leap year
            if (
                birthday.month == 2
                and birthday.day == 29
                and not (
                    today.year % 4 == 0
                    and (today.year % 100 != 0 or today.year % 400 == 0)
                )
            ):
                bday_this_year = bday_this_year.replace(
                    day=28
                )  # set birthday to 28th February

            if bday_this_year - today <= datetime.timedelta(
                days=7
            ):  # check if birthday is within 7 days

                if bday_this_year.weekday() == 5:  # check if birthday is on Saturday
                    congratulation_date = bday_this_year + datetime.timedelta(days=2)

                elif bday_this_year.weekday() == 6:  # check if birthday is on Sunday
                    congratulation_date = bday_this_year + datetime.timedelta(days=1)

                else:  # if birthday is on any other day
                    congratulation_date = bday_this_year

                bday_user["name"] = record.name  # add name and birthday to dictionary
                bday_user["congratulation_date"] = congratulation_date.strftime(
                    "%d.%m.%Y"
                )
                upcoming_birthdays.append(bday_user)  # append dictionary to list
        return upcoming_birthdays


class BaseView(ABC):
    @abstractmethod
    def phone(self, book: AddressBook):
        pass

    @abstractmethod
    def all(self, contacts):
        pass


class ConsoleView(BaseView):
    @input_error
    def phone(self, args, book: AddressBook) -> str:
        name = args[0]
        record = book.find(name)
        if record is None:
            return "Contact not found."
        phone_numbers = [str(phone) for phone in record.phones]
        return f"These are the phone numbers for {name}: {', '.join(phone_numbers)}"

    @input_error
    def all(self, book: AddressBook) -> None:
        """Function to print all contacts in the address book"""
        for record in book.data.values():
            print(record)


def main():
    """
    The function is controlling the cycle of command processing.
    """
    print("Welcome to the assistant bot!")
    view = ConsoleView()
    book = load_data()
    while True:
        # Getting the input from the user
        user_input = input("\nEnter a command: ")
        command, *args = parse_input(user_input)

        # Checking the command and calling the appropriate function
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(view.phone(args, book))

        elif command == "all":
            view.all(book)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            birthdays(book)

        # if the command is not recognized - print an error message
        else:
            print("Invalid command.")


def parse_input(user_input) -> tuple:
    """Function is finding a command in the input and returns it"""
    # Splitting the input into words, first word is a command, other words are arguments
    cmd, *args = user_input.split()
    # Converting the command to lower case and deleting extra spaces
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_contact(args, book: AddressBook) -> str:
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    try:
        phone = Phone(phone)
    except ValueError as e:
        return str(e)
    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        message = "Contact added."
    else:
        record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook) -> str:
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        return "Contact not found."

    try:
        old_phone_obj = Phone(old_phone)
        new_phone_obj = Phone(new_phone)
    except ValueError as e:
        return str(e)

    try:
        record.edit_phone(old_phone_obj, new_phone_obj)
    except ValueError as e:
        return str(e)

    return message


@input_error
def phone(args, book: AddressBook) -> str:
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    phone_numbers = [str(phone) for phone in record.phones]
    return f"These are the phone numbers for {name}: {', '.join(phone_numbers)}"


@input_error
def add_birthday(args, book: AddressBook) -> str:
    name, birthday, *_ = args
    record = book.find(name)
    message = "Birthday added."
    if record is None:
        return "Contact not found."
    try:
        record.add_birthday(birthday)
    except ValueError as e:
        return str(e)
    return message


def show_birthday(args, book: AddressBook) -> str:
    name = args[0]
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return f"{name}'s birthday is {record.birthday.value}"


def birthdays(book: AddressBook) -> str:
    birthdays_list = book.birthdays()
    for birthday in birthdays_list:
        print(
            f"Name: {birthday['name']}, Congratulation Date: {birthday['congratulation_date']}"
        )


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


if __name__ == "__main__":
    main()