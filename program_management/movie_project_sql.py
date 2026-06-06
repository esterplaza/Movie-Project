import random
import statistics
from datetime import datetime
import requests
import colorama
import matplotlib.pyplot as plot
from colorama import Fore, Style
import movie_storage.movie_storage_sql as storage
import main

API_KEY = "ENTER YOUR API"
HTML_TEMPLATE_PATH = "_static/index_template.html"

colorama.init(autoreset=True)


def app_header(user_id, user):
    """prints the title of the management menu and welcome message"""
    print()
    print(Fore.BLUE + Style.BRIGHT + f"Welcome Back {user}")
    print()
    print(Fore.BLUE + Style.BRIGHT + "********** My Movies Database **********")
    print()


def menu():
    """prints the management options for the menu"""
    print(Fore.BLUE + "Menu:")
    for key, value in MENU_ACTIONS.items():
        _, option, _ = value
        print(Fore.BLUE + f"{key} {option}")
    print()


def get_user_choice(max_choices):
    """requests the user to enter a choice"""
    while True:
        try:
            user_choice_local = int(
                input(Fore.YELLOW + f"Enter choice (0-" f"{max_choices}): ")
            )
            if 0 <= user_choice_local <= max_choices:
                print()
                break
            raise ValueError
        except ValueError:
            print()
            print(Fore.RED + "Invalid choice")
            print()
            menu()
    return user_choice_local


def list_movies(user_id, user):
    """
    prints the total number of movies and all the movies and ratings from
    the user's collection.
    """
    movies = storage.list_movies(user_id)
    number_of_movies = len(movies)
    print(Fore.BLUE + f"{user}: {number_of_movies} movies in total")
    for movie, info in movies.items():
        rating = info["rating"]
        year = info["year"]
        print(f"{movie} ({year}): {rating}")


def add_movie(user_id, user):
    """adds a movie, the release year, its rating and the url of the movie poster
     to the user´s collection in a database, the information is
    fetched from the IMDb database through the omdbapi"""
    movies = storage.list_movies(user_id)
    while True:
        new_movie = input(Fore.YELLOW + f"{user}, Enter new movie name: ")
        if new_movie == "":
            print(Fore.RED + "Movie name must not be empty.")
        else:
            break
    try:
        url = f"https://www.omdbapi.com/?t={new_movie}&apikey={API_KEY}"
        response = requests.get(url, timeout=(5, 30))
        add_new_movie = response.json()["Title"]
        add_year = response.json()["Year"]
        add_rating = response.json()["imdbRating"]
        add_poster = response.json()["Poster"]
        if add_new_movie in movies:
            print(Fore.RED + "Movie", end=" ")
            print(Fore.YELLOW + f'"{new_movie}"', end=" ")
            print(Fore.RED + "already exist!")
        else:
            storage.add_movie(add_new_movie, add_year, add_rating, add_poster, user_id)
    except KeyError:
        print(Fore.RED + "The title was not found, try again")
    except requests.Timeout:
        print(Fore.RED + "Request timed out")
    except requests.RequestException as e:
        print(Fore.RED + f"Request failed:, {e}")


def delete_movie(user_id, user):
    """deletes a movie from the user's collection in a database"""
    movie_to_delete = input(Fore.YELLOW + f"{user}, Enter movie name to delete: ")
    movies = storage.list_movies(user_id)
    if movie_to_delete in movies:
        storage.delete_movie(movie_to_delete, user_id)
    else:
        print(Fore.RED + f"Movie {movie_to_delete} doesn't exist!")


def update_movie(user_id, user):
    """updates the rating of a movie from the user's collection in a database"""
    movie_to_be_updated = input(Fore.YELLOW + f"{user}, Enter movie name: ")
    movies = storage.list_movies(user_id)
    if movie_to_be_updated in movies:
        try:
            note_for_existing_movie = input(Fore.YELLOW + "Enter movie note: ")
            storage.update_movie(movie_to_be_updated, note_for_existing_movie, user_id)
        except ValueError:
            print(Fore.RED + "Please enter a valid rating")

    else:
        print(Fore.RED + f"Movie {movie_to_be_updated} doesn't exist!")


def list_ratings(dict_movies):
    """takes the user's collection of movies from a database
    and returns a list of all the ratings"""
    list_of_ratings = []
    for _, info in dict_movies.items():
        rating = info["rating"]
        list_of_ratings.append(rating)
    return list_of_ratings


def stats(user_id, user):
    """prints the statistics of the dictionary"""
    movies = storage.list_movies(user_id)
    list_of_ratings = list_ratings(movies)
    average_rating = round(statistics.mean(list_of_ratings), 2)
    print(f"Average rating: {average_rating}")
    median_rating = round(statistics.median(list_of_ratings), 2)
    print(f"Median rating: {median_rating}")
    for movie, info in movies.items():
        rating = info["rating"]
        if rating == max(list_of_ratings):
            print(f"Best Movie: {movie}, {rating}")
        if rating == min(list_of_ratings):
            print(f"Worst Movie: {movie}, {rating}")


def random_movie(user_id, user):
    """chooses a random movie"""
    movies = storage.list_movies(user_id)
    random_movie_local = random.choice(list(movies.keys()))
    random_rating_local = movies[random_movie_local]["rating"]
    print(
        f"{user}, Your movie for tonight: {random_movie_local}, it's rated {random_rating_local}"
    )


def editing_distance(movie_original, movie_user):
    """calculates the minimum editing distance between two strings"""
    editing_distance_matrix = []
    rows = len(movie_original) + 1
    cols = len(movie_user) + 1
    for row in range(rows):
        editing_distance_matrix.append([0] * cols)
    for row in range(rows):
        editing_distance_matrix[row][0] = row
    for col in range(cols):
        editing_distance_matrix[0][col] = col
    for row in range(1, rows):
        for col in range(1, cols):
            if movie_original[row - 1] == movie_user[col - 1]:
                editing_distance_substitution = editing_distance_matrix[row - 1][
                    col - 1
                ]
            else:
                editing_distance_substitution = (
                    editing_distance_matrix[row - 1][col - 1] + 1
                )
            editing_distance_delection = editing_distance_matrix[row - 1][col] + 1
            editing_distance_insertion = editing_distance_matrix[row][col - 1] + 1
            editing_distance_matrix[row][col] = min(
                editing_distance_delection,
                editing_distance_insertion,
                editing_distance_substitution,
            )
    return editing_distance_matrix[row][col]


def is_movie_in_movies(user_movie, dicc_movies):
    """checks if the movie entered by the user is in the dictionary of
    movies"""
    answer = False
    for movie, info in dicc_movies.items():
        movie_low = movie.lower()
        if user_movie in movie_low:
            rating = info["rating"]
            print(f"{movie}, {rating}")
            answer = True
    return answer


def combination_of_words(title):
    """returns a list of the possible combinations of the words of a movie
    title, the order of the words are not changed for the combinations"""
    words_in_movie = title.split()
    parts_of_movie_names = words_in_movie.copy()
    if len(words_in_movie) >= 2:
        for i in range(len(words_in_movie) - 1):
            last_part = words_in_movie[i]
            for j in range(i + 1, len(words_in_movie)):
                parts_of_movie_names.append(last_part + " " + words_in_movie[j])
                last_part += " " + words_in_movie[j]
    return parts_of_movie_names


def coincidence(list_of_words, word_to_search):
    """checks if there is a coincidence (max. editing distance of 2) between
    two strings"""
    for word in list_of_words:
        if 0 <= editing_distance(word_to_search, word) <= 2:
            return True
    return False


def search_movie(user_id, user):
    """searches a movie by its title in a user's collection in a
    database of movies"""
    movies = storage.list_movies(user_id)
    movie_to_search = input(Fore.YELLOW + f"{user}, Enter part of movie name: ")
    print()
    movie_to_search_low = movie_to_search.lower()
    counter = 0
    if not is_movie_in_movies(movie_to_search_low, movies):
        print(Fore.RED + "The movie ", end="")
        print(Fore.YELLOW + f'"{movie_to_search}"', end="")
        print(Fore.RED + " does not exist. ", end="")
        for movie in movies.keys():
            movie_low = movie.lower()
            combination_of_words_in_movie = combination_of_words(movie_low)
            if coincidence(combination_of_words_in_movie, movie_to_search_low):
                if counter == 0:
                    print(Fore.RED + "Did you mean:")
                    counter += 1
                print(movie)


def sorted_rating(user_id, user):
    """prints the movies sorted by rating in descending order from a
    user's collection in a database"""
    movies = storage.list_movies(user_id)
    sort_and_print(movies, "rating", True)


def sorted_year(user_id, user):
    """prints the movies sorted by year from a user´s collection in a database.
    The user is asked to decide the kind of order"""
    movies = storage.list_movies(user_id)
    while True:
        try:
            order = input(
                Fore.YELLOW + f"{user}, Do you want the latest movies first? (Y/N) "
            )
            print()
            order_low = order.lower()
            if order_low in ("y", "n"):
                break
            raise ValueError
        except ValueError:
            print(Fore.RED + "Please enter 'Y' or 'N'")
    order_reverse = order_low == "y"
    sort_and_print(movies, "year", order_reverse)


def sort_and_print(movies_db, value_to_sort, reverse):
    """
    creates a sorted list of the movie titles based on the value to
    sort. It prints the list of movies, year and rating in the desired order.
    """
    try:
        dict_sorted = sorted(
            movies_db.keys(), key=lambda k: movies_db[k][value_to_sort], reverse=reverse
        )
        for movie in dict_sorted:
            rating = movies_db[movie]["rating"]
            year = movies_db[movie]["year"]
            print(f"{movie} ({year}): {rating}")
    except TypeError:
        print(Fore.RED + "Please check the values in the database.")
        print(Fore.RED + "Maybe some of the value to sort is not in the right format")


def is_valid_year(year):
    """checks if year is valid (0-current year)"""
    current_year = datetime.now().year
    return 0 <= year <= current_year


def is_valid_rating(rating):
    """checks if rating is valid (0-10)"""
    return 0 <= rating <= 10


def valid_filter_input(prompt, filter_modus):
    """checks if the user input for the filter is valid"""
    default_values = {"min_rating": 0, "start_year": 0, "end_year": datetime.now().year}
    while True:
        user_input = input(Fore.YELLOW + prompt)
        variable_to_print = ""
        if user_input == "":
            filter_option = default_values.get(filter_modus)
            break
        try:
            if filter_modus == "min_rating":
                variable_to_print = "rating"
                filter_option = float(user_input)
                if not is_valid_rating(filter_option):
                    raise ValueError
                break
            if filter_modus in ("start_year", "end_year"):
                variable_to_print = "year"
                filter_option = int(user_input)
                if not is_valid_year(filter_option):
                    raise ValueError
                break
        except ValueError:
            print(Fore.RED + f"Invalid input. Please enter a valid {variable_to_print}")
    return filter_option


def filter_movies(user_id, user):
    """prints a list of movies, year and rating from the data in user´s
    collection in a database.
    The user is asked to enter the minimum rating, the start year and the
    end year to print only the movies within this characteristics"""
    movies = storage.list_movies(user_id)
    user_input_min_rating = (
        f"{user}, Enter minimum rating (leave blank for no minimum rating): "
    )
    min_rating = valid_filter_input(user_input_min_rating, "min_rating")
    user_input_start_year = "Enter start year (leave blank for no start year): "
    start_year = valid_filter_input(user_input_start_year, "start_year")
    user_input_end_year = "Enter end year (leave blank for no end year): "
    end_year = valid_filter_input(user_input_end_year, "end_year")
    print(Fore.BLUE + "Filtered movies")
    for movie, info in movies.items():
        movie_rating = info.get("rating")
        movie_year = info.get("year")
        if movie_rating >= min_rating:
            if start_year <= movie_year <= end_year:
                print(f"{movie} ({movie_year}): {movie_rating}")


def histogram_rating(user_id, user):
    """prints a histogram of the movie rating from a user´s collection database"""
    movies = storage.list_movies(user_id)
    file_name_histogram = input(
        Fore.YELLOW + "Enter file name to save the rating histogram: "
    )
    ratings = list_ratings(movies)
    plot.hist(ratings, bins=range(0, 11, 1), color="skyblue", edgecolor="black")
    plot.xlabel("Movie Rating")
    plot.ylabel("Number of Movies")
    plot.title(f"Movie Rating Distribution for {user}")
    plot.savefig(f"{file_name_histogram}.png", dpi=300, bbox_inches="tight")
    plot.show()


def read_html_template(html_path):
    """reads a html template file"""
    with open(html_path, "r", encoding="utf-8") as html_file:
        return html_file.read()


def serialize_movie(title, info):
    """creates a html card for an item"""
    year = info.get("year")
    poster = info.get("poster")
    rating = info.get("rating")
    note = info.get("note")
    output = ""
    output += "<li>\n"
    output += '<div class="movie">\n'
    output += f'<img class="movie-poster" src="{poster}">\n'
    if note:
        output += f'<div class="note">{note}</div>\n'
    output += f'<div class="movie-title">{title}</div>\n'
    output += f'<div class="movie-year">{year}</div>\n'
    output += f'<div class="movie-rating">Rating: {rating}</div>\n'
    output += "</div>\n"
    output += "</li>\n"
    return output


def create_html(data, user):
    """
    adds the web title and for each movie the movie title, the movie year and
    the movie poster, all in a given html template
    """
    movie_grid = ""
    for movie, info in data.items():
        movie_grid += serialize_movie(movie, info)
    html_data = read_html_template(HTML_TEMPLATE_PATH)
    title = f"{user}'s favorite Movies"
    html_data = html_data.replace("__TEMPLATE_TITLE__", title)
    html_data = html_data.replace("__TEMPLATE_MOVIE_GRID__", movie_grid)
    return html_data


def write_new_html(html_string, filename):
    """writes a new html file"""
    with open(filename, "w", encoding="utf-8") as new_html_file:
        new_html_file.write(html_string)


def generate_website(user_id, user):
    """generates a website with the information of a user's collection
    in a database"""
    movies = storage.list_movies(user_id)
    html_movies = create_html(movies, user)
    write_new_html(html_movies, f"_static\\index_{user}.html")
    print(Fore.BLUE + f"Website was generated successfully for {user}")


def exit_program(user_id, user):
    """prints bye"""
    print()
    print(Fore.BLUE + f"Bye {user}!")
    print()


def switch_user(user_id, user):
    """prints bye and redirects to the main function"""
    print()
    print(Fore.BLUE + f"Bye {user}!")
    print()
    main.main()


def continue_application():
    """checks if the user wants to continue"""
    print()
    user_continue_choice = input(Fore.YELLOW + "Press enter to continue ")
    print()
    return "" in user_continue_choice


MENU_ACTIONS = {
    0: (exit_program, "Exit", False),
    1: (list_movies, "List movies", True),
    2: (add_movie, "Add movie", True),
    3: (delete_movie, "Delete movie", True),
    4: (update_movie, "Update movie", True),
    5: (stats, "Stats", True),
    6: (random_movie, "Random movie", True),
    7: (search_movie, "Search movie", True),
    8: (sorted_rating, "Movies sorted by rating", True),
    9: (sorted_year, "Movies sorted by year", True),
    10: (filter_movies, "Filter movies", True),
    11: (histogram_rating, "Create Rating Histogram", True),
    12: (generate_website, "Generate website", True),
    13: (switch_user, "Switch User", False),
}


def program_management(user):
    user_id = storage.select_user_id(user)["id"]
    app_header(user_id, user)
    carry_on = True
    while carry_on:
        menu()
        max_choices = len(MENU_ACTIONS) - 1
        choice = get_user_choice(max_choices)
        action, _, carry_on = MENU_ACTIONS.get(choice)
        action(user_id, user)
        if carry_on:
            continue_application()
