import requests
import json

API_KEY = ""
API_FILE_PATH = "./API.txt"
TIMEOUT_TIME = 10
CITY_URL = "https://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_RESULT_LIMIT = 5
FAVORITE_FILE_PATH = "./Favorites.json"
MAX_FAVORITES = 3

def main():
    global API_KEY

    print("Hello! Welcome to the open weather CLI tool.")

    # Checks to see if the API Key has been manually updated in this main file, otherwise tries to read it from the dedicated API key file
    if API_KEY == "":
        with open(API_FILE_PATH, "r", encoding="utf-8") as file:
            API_KEY = file.read().strip()
    # If the dedicated API Key file does not contain the API Key, prompt the user for it and test it until we get a valid key
    if API_KEY == "":
        is_valid_api_key = False
        print("No stored API Key found!")
        while is_valid_api_key == False:
            API_KEY = input("Please enter the API key from the email!: ")
            is_valid_api_key = test_api_key()
        # Save the API Key to the dedicated file once we know that it works
        with open(API_FILE_PATH, "w", encoding="utf-8") as file:
            file.write(API_KEY)
        print("API Key is valid! Now saving to local file!")

    # Main loop of the program
    while True:
        print("\n1: Look up the weather in a city by name.")
        print("2: Add a city to favorites.")
        print("3: Remove a city from favorites.")
        print("4: Display the weather in your favorited cities.")
        print("5: Close the program.")
        action = input("Please select what action you would like to take by choosing the corresponding number from the list above: ")
        match action:
            case "1":
                check_city_weather()
            case "2":
                add_city_to_favorites()
            case "3":
                remove_city_from_favorites()
            case "4":
                list_favorite_weathers()
            case "5":
                exit()
            case _:
                "Invalid selection. Please Try again"

def test_api_key():
    # Helper function to test if the API Key gets a valid response
    # Returns true if valid response is received and false otherwise
    try:
        response = requests.get(
            WEATHER_URL,
            params={
                "lat": 51.5073,
                "lon": -0.1277,
                "appid": API_KEY,
            },
            timeout=TIMEOUT_TIME,
        )
        return response.status_code == 200
    except Exception:
        return False

def check_city_weather():

    # Get info about what city the user would like the weather of
    city_name = input("\nPlease enter the name of the city you would like weather details for (do not add state or country) and press enter to submit: ")
    city_state = input("If desired, please enter the state in which the city resides (ex: PA, NY, etc.) and press enter to submit. If not desired please submit a blank line: ")
    city_country = input("If desired, please enter the country in which the city resides (ex: US, GB, etc.) and press enter to submit. If not desired please submit a blank line: ")

    limit = input("Please enter how many potential matches you would like to choose from and press enter to submit. If no amount is entered, the default of 5 will be used: ")

    # Build the city query name according to the API specifications
    city_query = city_name
    if city_state != "":
        city_query = city_query + ", " + city_state
    if city_country != "":
        city_query = city_query + ", " + city_country

    # Validate that the user entered an integer for the limit, if not the default is used
    try:
        limit = int(limit)
    except Exception:
        possible_cities = request_cities(city_query)
    else:
        possible_cities = request_cities(city_query, limit)

    # If possible cities is None, that means there was an error with the API call and we can not proceed
    if possible_cities is None:
        return

    if len(possible_cities) == 0:
        print("\nNo matching cities found! Please try again.")
        return

    choice = handle_city_selection(possible_cities)

    # Validate that the chosen city exists, get the weather from the api, and show it to the user
    if choice is not None:
        weather = request_weather(choice['lat'], choice['lon'])

        # If weather is none, that means there was an error with the api and we can not show the weather
        if weather is not None:
            print_weather(choice, weather)

        # Wait for the user to be ready to return to the main menu
        input("Press Enter to return to the main menu")

def add_city_to_favorites():

    # Load the favorited cities from the favorites file
    with open(FAVORITE_FILE_PATH, "r", encoding="utf-8") as file:
        favorites = json.load(file)

    # Check to make sure the user has not added too many favorites and if they have dont allow them to add more
    if len(favorites) >= MAX_FAVORITES:
        print("\nYou have reached the maximum amount of favorites! Please remove one before adding another.")
        return

    # Get info about what city the user would like to add to their favorites
    city_name = input("\nPlease enter the name of the city you would like to add to favorites (do not add state or country) and press enter to submit: ")
    city_state = input("If desired, please enter the state in which the city resides (ex: PA, NY, etc.) and press enter to submit. If not desired please submit a blank line: ")
    city_country = input("If desired, please enter the country in which the city resides (ex: US, GB, etc.) and press enter to submit. If not desired please submit a blank line: ")

    limit = input("Please enter how many potential matches you would like to choose from and press enter to submit. If no amount is entered, the default of 5 will be used: ")

    # Build the city query name according to the API specifications
    city_query = city_name
    if city_state != "":
        city_query = city_query + ", " + city_state
    if city_country != "":
        city_query = city_query + ", " + city_country

    # Validate that the user entered an integer for the limit, if not the default is used
    try:
        limit = int(limit)
    except Exception:
        possible_cities = request_cities(city_query)
    else:
        possible_cities = request_cities(city_query, limit)

    # If possible cities is None, that means there was an error with the API call and we can not proceed
    if possible_cities is None:
        return

    if len(possible_cities) == 0:
        print("\nNo matching cities found! Please try again.")
        return

    choice = handle_city_selection(possible_cities)

    # If their choice is valid, store the favorited city in the favorites file
    if choice is not None:
        favorites.append(choice)
        with open(FAVORITE_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(favorites, file)

def remove_city_from_favorites():

    # Load the favorited cities from the favorites file
    with open(FAVORITE_FILE_PATH, "r", encoding="utf-8") as file:
        favorites = json.load(file)

    # Check to make sure the user has favorites to remove before giving them options
    if len(favorites) == 0:
        print("\nYou have no favorites to remove!")
        return

    # List out the cities that the user can remove
    print()
    i = 1
    for city in favorites:
        print(str(i) + ": " + format_city(city))
        i += 1

    # Prompt the user for which city they would like to remove
    choice = input("Please enter the number matching the city you would like to remove from your favorites. If you would not like to remove any of these cities, please submit a blank line: ")

    # Validate that the chosen city exists and can be removed
    if choice == "":
        return
    try:
        choice = int(choice)
    except Exception:
        print("\n" f"Error: '{choice}' is not a valid option. Please Try again.")
    else:
        choice_index = choice - 1
        if choice_index < 0 or choice_index >= len(favorites):
            print("\n" f"Error: '{choice}' is not a valid option. Please Try again.")
        else:
            print("\nYou have removed: " + format_city(favorites[choice_index]))
            # Remove the chosen city
            favorites.pop(choice_index)
            # Update the favorites file with the removed city
            with open(FAVORITE_FILE_PATH, "w", encoding="utf-8") as file:
                json.dump(favorites, file)

def list_favorite_weathers():

    # Load the favorited cities from the favorites file
    with open(FAVORITE_FILE_PATH, "r", encoding="utf-8") as file:
        favorites = json.load(file)

    # Make sure the user has favorited cities to show the weather of
    if len(favorites) <= 0:
        print("\nYou have no favorites to show the weather of. Try adding some!")
        return

    # Get and show the weather of the users favorited cities using the two helper functions
    for city in favorites:
        weather = request_weather(city['lat'], city['lon'])

        # If weather is none, that means there was an error with the api and we can not show the weather
        if weather is not None:
            print_weather(city, weather)

    # Wait for the user to be ready to return to the main menu
    input("Press Enter to return to the main menu")

def handle_city_selection(possible_cities: list):

    # List the possible choices of cities
    print("")
    i = 1
    for city in possible_cities:
        print(str(i) + ": " + format_city(city))
        i += 1

    # Collect and validate the users choice
    choice = input("Please enter the number matching your desired city. If none of the cities match your desired city, please submit a blank line: ")
    try:
        choice = int(choice)
    # Validate that the user entered an integer as their choice
    except Exception:
        print("\n" f"Error: '{choice}' is not a valid option. Please Try again. If you did not see your desired city, consider increasing the number of potential matches you can choose from")
    else:

        choice_index = choice - 1

        # Validate that the user's choice is within the range of possible cities
        if choice_index < 0 or choice_index >= len(possible_cities):
            print("\n" f"Error: '{choice}' is not a valid option. Please Try again. If you did not see your desired city, consider increasing the number of potential matches you can choose from")
        else:
            # Display the user's choice to them and return it
            print("\nYou have selected: " + format_city(possible_cities[choice_index]))
            return possible_cities[choice_index]

def format_city(city):
    # Helper function for converting cities into human-readable strings
    return f"{city['name']} " f"({city['state']}, " f"{city['country']})"

def request_cities(name: str, result_limit: int = DEFAULT_RESULT_LIMIT):
    # Helper function to get cities from the open weather API
    # Returns a list of possible cities that match the query from the API (when successful) or none when there is an error communicating with the API

    try:
        params = {
            "q": name,
            "limit": result_limit,
            "appid": API_KEY,
        }

        response = requests.get(CITY_URL, params=params, timeout=TIMEOUT_TIME)
        response.raise_for_status()
        return response.json()

    # Catch any errors that might come from a failed response
    except Exception:
        print("\n Error retrieving cities from the open weather API please check your connection and/or try again later")
        return

def request_weather(lat: float, lon: float):
    # Helper function that returns the weather at a specified latitude and longitute
    # Returns the weather info object received from the api (when successful) or none when there is an error communicating with the API
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "imperial",
        }

        response = requests.get(WEATHER_URL, params=params, timeout=TIMEOUT_TIME)
        response.raise_for_status()
        return response.json()

    # Catch any errors that might come from a failed response
    except Exception:
        print("\n Error retrieving weather from the open weather API please check your connection and/or try again later")
        return

def print_weather(city: str, weather):
    # Helper function that shows information about a city's weather
    print("\nThe current weather in " + format_city(city) + " is: " f"{weather['weather'][0]['description']}")
    print("Temperature: " f"{weather['main']['temp']}°F")
    print("Temperature (feels like): " f"{weather['main']['feels_like']}°F")
    print("Windspeed: " f"{weather['wind']['speed']} mph")
    print("Humidity: " f"{weather['main']['humidity']}%")
    print("Pressure: " f"{weather['main']['pressure']} hPa")

main()