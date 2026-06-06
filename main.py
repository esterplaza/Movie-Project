import sys
from colorama import Fore, Style
import movie_storage.movie_storage_sql as storage
import program_management.movie_project_sql as mov


def menu_user():
    """
    Prints the user menu. There is the current list of users and the option
    to add a new one. It returns the maximum number of choices that it lists,
    that depends on the users that are already in the users list.
    """
    print(Fore.BLUE + "Select a user:")
    users_data = storage.list_users()
    print(Fore.BLUE + "0. Exit")
    last_user = 0
    for user_id, data in users_data.items():
        print(Fore.BLUE + f"{user_id}. {data["name"]}")
        last_user = user_id
    max_user_choices = last_user + 1
    print(Fore.BLUE + f"{max_user_choices}. Create new user")
    print()
    return max_user_choices


def main_header():
    """
    Prints the header of the application
    """
    print(Fore.BLUE + Style.BRIGHT + "Welcome to the Movie App! 🎬")
    print(Fore.BLUE + Style.BRIGHT + "----------------------------")


def create_new_user():
    """
    Asks the user to enter the name and calls the function that inserts the
    new user in the user's list. It returns the new user name.
    """
    user_name = input(Fore.BLUE + "Enter your name: ")
    storage.add_new_user(user_name)
    return user_name


def main():
    main_header()
    max_user_choices = menu_user()
    main_choice = mov.get_user_choice(max_user_choices)
    if main_choice == 0:
        sys.exit()
    elif main_choice == max_user_choices:
        user_name = create_new_user()
    else:
        users_data = storage.list_users()
        user_name = users_data[main_choice]["name"]
    mov.program_management(user_name)


if __name__ == "__main__":
    main()
