# V2 To-do's (1) Format backlog list output with tabulate (2) Apply pyfiglet to opening message (3) Autofill game data with IGDB API (4) Implement a GUI with Flask
"""
This module implements a Game Backlog Manager, allowing users to manage their video game collection.
It provides functionalities to add, remove, sort, and display games in the backlog, along with user management capabilities.

Classes:
    Game: Represents a single video game with various attributes.
    Backlog: Manages a collection of games for a user.
    User: Represents a user of the application and manages their game backlog.

Exceptions:
    ValidationError: Base class for exceptions related to validation errors.
    InvalidGameDataError: Raised for errors in game data structure or content.
    FileIOError: Raised for errors during file I/O operations.
    InvalidDateError: Raised for errors related to date format or value.
    DuplicateUsernameError: Raised when a duplicate username is encountered.

Functions:
    main(): The main function of the script, handling the primary user interface.
    optional_int_input(prompt, min_value): Prompts for optional integer input.
    optional_string_input(prompt): Prompts for optional string input.
    optional_time_input(prompt): Prompts for time input in HH:MM format.
    mandatory_string_input(prompt): Prompts for mandatory string input.
    create_new_user(): Handle new user creation process
    load_existing_user(): Handle existing user loading process
    manage_backlog(user): Manage the game backlog for a user.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import date
import json
import os


def main():
    """
    Execute the Game Backlog Manager application.

    This function initiates the user interface of the application, allowing for various user interactions.
    Users can create new profiles or load existing ones, and manage their game backlog with options like
    adding, removing, sorting games, and more. The application runs in a loop until the user decides to exit.

    The main loop consists of three levels:
    1. Application Loop: Manages the overall running state of the application.
    2. User Management Loop: Handles user profile creation, loading, and switching.
    3. Backlog Management Loop: Offers various options to manage the game backlog.
    """
    # Main application loop
    running = True
    while running:
        print("Welcome to the Game Backlog Manager!")

        # User management loop
        user = None
        while user is None:
            choice = input(
                "Do you want to create a new user, load an existing user, or exit the program? [new/load/exit]: "
            )
            # Validate user choice
            if choice.lower() not in ["new", "load", "exit"]:
                print("Invalid choice, please enter 'new', 'load', or 'exit'.")
                continue

            # Create a new user profile
            if choice.lower() == "new":
                user = create_new_user()

            # Load an existing user profile
            elif choice.lower() == "load":
                user = load_existing_user()

            # Exit the application
            elif choice.lower() == "exit":
                print("Goodbye!")
                running = False
                break

        # Enter the backlog management loop if a user is selected
        if user:
            running, user = manage_backlog(user)


# Define custom exceptions for specific validation errors
class ValueError(Exception):
    """Exception raised for errors in the value."""

    pass


class ValidationError(Exception):
    """Base class for exceptions related to validation errors."""

    pass


class InvalidGameDataError(ValidationError):
    """Exception raised for errors in the game data structure or content."""

    pass


class FileIOError(ValidationError):
    """Exception raised for errors during file input/output operations."""

    pass


class InvalidDateError(ValidationError):
    """Exception raised for errors related to date format or value."""

    pass


class DuplicateUsernameError(ValidationError):
    """Exception raised when a duplicate username is encountered."""

    pass


@dataclass
class Game:
    """Represents a single video game with various attributes.

    Attributes:
        title (str): The title of the game.
        genre (str): The genre of the game.
        release_year (int): The year the game was released.
        date_added (date): The date the game was added to the backlog. Defaults to today's date.
        time_to_beat (tuple[int, int]): The estimated time to beat the game in hours and minutes.
        priority (int): The priority of the game in the backlog.
    """

    title: str
    genre: Optional[str] = None
    release_year: Optional[int] = None
    date_added: date = field(default_factory=lambda: date.today())
    time_to_beat: Optional[tuple[int, int]] = None
    priority: Optional[int] = None

    def __post_init__(self):
        """Post-initialization processing to validate the data of the Game instance."""
        # Validate title as a non-empty string
        if not self.title or not isinstance(self.title, str):
            raise InvalidGameDataError("Title must be a non-empty string.")

        # Validate that genre, if provided, is a string
        if self.genre is not None and not isinstance(self.genre, str):
            raise InvalidGameDataError("Genre must be a string.")

        # Validate that release year, if provided, is a positive integer
        if self.release_year is not None and (
            not isinstance(self.release_year, int) or self.release_year <= 0
        ):
            raise InvalidGameDataError("Release year must be a positive integer.")

        # Validate and set date added
        if self.date_added is None:
            self.date_added = date.today()
        elif not isinstance(self.date_added, date):
            raise InvalidDateError("Date added must be a valid date.")
        if self.date_added > date.today() or self.date_added.year < 1950:
            raise InvalidDateError(
                "Date added must be between 1950 and today, inclusive."
            )

        # Validate that time to beat, if provided, is a tuple of two non-negative integers
        if self.time_to_beat is not None and (
            not isinstance(self.time_to_beat, tuple)
            or len(self.time_to_beat) != 2
            or not all(isinstance(num, int) for num in self.time_to_beat)
            or self.time_to_beat[0] < 0
            or self.time_to_beat[1] < 0
            or self.time_to_beat[1] >= 60
        ):
            raise ValidationError(
                "Time to beat must be a tuple of two non-negative integers, with minutes less than 60."
            )

        # Validate that priority, if provided, is a non-negative integer
        if self.priority is not None:
            if not isinstance(self.priority, int) or self.priority < 0:
                raise ValidationError("Priority must be a non-negative integer.")

    def to_dict(self) -> dict:
        """Converts the Game instance into a dictionary for serialization.

        Returns:
            dict: A dictionary representation of the Game instance.
        """
        game_dict = vars(self)
        # Convert date_added to string if it's not None
        if isinstance(game_dict["date_added"], date):
            game_dict["date_added"] = game_dict["date_added"].isoformat()
        return game_dict

    @staticmethod
    def from_dict(data: dict) -> "Game":
        """Deserialize a dictionary into a Game instance, with validation.

        Args:
            data (dict): The dictionary containing game data.

        Returns:
            Game: A new Game instance based on the data provided.

        Raises:
            InvalidGameDataError: If required keys are missing in the data.
            InvalidDateError: If the date format is invalid.
        """
        # Check for required keys in the data
        required_keys = [
            "title",
            "genre",
            "release_year",
            "date_added",
            "time_to_beat",
            "priority",
        ]
        if not all(key in data for key in required_keys):
            raise InvalidGameDataError("Missing required game data keys.")

        # Convert date_added from string to date object
        try:
            data["date_added"] = date.fromisoformat(data["date_added"])
        except ValueError:
            raise InvalidDateError("Invalid date format in game data.")

        # Handle time_to_beat based on its type in the data
        time_to_beat = data.get("time_to_beat")
        if time_to_beat is not None:
            if isinstance(time_to_beat, list) and len(time_to_beat) == 2:
                hours, minutes = time_to_beat
            elif isinstance(time_to_beat, str):
                try:
                    hours, minutes = map(int, time_to_beat.split(":"))
                except ValueError:
                    raise InvalidGameDataError("Invalid time to beat format.")
            else:
                raise InvalidGameDataError("Invalid time to beat format.")

            if hours < 0 or minutes < 0 or minutes >= 60:
                raise InvalidGameDataError("Invalid time to beat format.")
            data["time_to_beat"] = (hours, minutes)

        # Create and return a Game instance
        return Game(**data)


class Backlog:
    """
    Represents a collection of games in a user's backlog.

    This class manages operations such as adding, removing, saving, and loading games.

    Attributes:
        games (List[Game]): A list of Game instances in the backlog.
        file_loaded (bool): Indicates whether the backlog file has been loaded.
        filename (str): The filename used for saving and loading the backlog.

    Methods:
        __init__(filename, games): Initialize a new backlog instance.
        __str__(): String representation of the backlog.
        __repr__(): Formal string representation of the backlog instance.
        games(): Property to get the list of games, loading from file if necessary.
        games(value): Property setter to set the list of games.
        add_game(game): Add a new game to the backlog.
        remove_game(game): Remove a game from the backlog.
        game_count(): Return the number of games in the backlog.
        save_to_file(filename): Save the backlog to a JSON file.
        load_from_file(filename): Load the backlog from a JSON file.
        sort_backlog(criterion, reverse): Sort the games in the backlog.
    """

    def __init__(self, filename: str, games: Optional[List[Game]] = None):
        """Initialize a new backlog instance.

        Args:
            filename (str): The filename to use for saving and loading the backlog.
            games (Optional[List[Game]]): A list of games to add to the backlog.
        """
        self.games = games if games is not None else []
        self.file_loaded = False
        self.filename = filename

    def __str__(self) -> str:
        """Return a string representation of the backlog.

        Returns:
            str: A string that lists the titles of all games in the backlog.
        """
        if not self._games:
            return "Backlog: [Empty]"
        games_list = ", ".join(game.title for game in self._games)
        return f"Backlog: [{games_list}]"

    def __repr__(self) -> str:
        """Return a formal string representation of the backlog instance.

        Returns:
            str: A string representation of the Backlog instance for debugging.
        """
        return f"Backlog(games={self._games!r})"

    @property
    def games(self) -> List[Game]:
        """Returns the list of games in the backlog.

        This property ensures that the backlog is loaded from the file (if not already loaded)
        before returning the games list.

        Returns:
            List[Game]: A list of Game instances in the backlog.
        """
        if not self.file_loaded:
            self.load_from_file(self.filename)
            self.file_loaded = True
        return self._games

    @games.setter
    def games(self, value: List[Game]):
        """Set the list of games in the backlog.

        Validates that all items in the list are instances of the Game class.

        Args:
            value (List[Game]): A new list of games to replace the existing one.

        Raises:
            ValidationError: If any item in the list is not an instance of Game.
        """
        if not all(isinstance(game, Game) for game in value):
            raise ValidationError(
                "All items in the list must be instances of the Game class."
            )
        self._games = value

    def add_game(self, game: Game):
        """Add a new game to the backlog and save changes.

        Args:
            game (Game): The game to be added to the backlog.

        Raises:
            ValidationError: If the provided game is not an instance of Game.
        """
        if not isinstance(game, Game):
            raise ValidationError(
                "Can only add instances of the Game class to the backlog."
            )
        self._games.append(game)
        self.save_to_file(self.filename)  # Automatically save after adding

    def remove_game(self, game: Game):
        """Remove a game from the backlog.

        If the game is not found in the backlog, a message is printed.

        Args:
            game (Game): The game to be removed from the backlog.
        """
        try:
            self._games.remove(game)
        except ValueError:
            print(f"Game '{game.title}' not found in backlog.")
        self.save_to_file(self.filename)  # Automatically save after removing

    def game_count(self) -> int:
        """Return the number of games in the backlog.

        Returns:
            int: The total number of games in the backlog.
        """
        return len(self._games)

    def save_to_file(self, filename: str):
        """Save the backlog to a JSON file.

        Args:
            filename (str): The filename for the file where the backlog will be saved.

        Raises:
            FileIOError: If an error occurs during file writing.
        """
        try:
            with open(filename, "w") as file:
                json.dump([game.to_dict() for game in self._games], file, indent=4)
        except IOError as e:
            raise FileIOError(f"An error occurred while saving the file: {e}")

    def load_from_file(self, filename: str):
        """Load the backlog from a JSON file.

        Args:
            filename (str): The filename of the file from which to load the backlog.

        Raises:
            FileIOError: If an error occurs during file reading.
        """
        try:
            with open(filename, "r") as file:
                file_content = file.read()
                if not file_content:
                    self._games = []
                else:
                    self._games = [
                        Game.from_dict(data) for data in json.loads(file_content)
                    ]
        except IOError as e:
            raise FileIOError(f"An error occurred while loading the file: {e}")
        except json.JSONDecodeError as e:
            raise FileIOError(f"Invalid JSON format in the file: {e}")

    def sort_backlog(self, criterion: str, reverse: bool = False):
        """Sort the games in the backlog based on a given criterion.

        Args:
            criterion (str): The attribute of the Game class to sort by (e.g., 'title', 'release_year').
            reverse (bool): If set to True, sorts in descending order. Default is False (ascending order).

        Raises:
            ValueError: If the provided criterion is not a valid attribute of Game.
        """
        if criterion not in [
            "title",
            "genre",
            "release_year",
            "priority",
            "time_to_beat",
            "date_added",
        ]:
            raise ValueError(f"Invalid sorting criterion: {criterion}")

        def get_sort_key(game):
            value = getattr(game, criterion)
            if value is None:
                if criterion in ["title", "genre"]:
                    return ""
                elif criterion in ["release_year", "priority"]:
                    return 0
                elif criterion == "time_to_beat":
                    return (0, 0)
                else:
                    return value  # For 'date_added' and other non-string, non-numeric attributes

            if isinstance(value, str):
                return value.lower()
            else:
                return value

        self._games.sort(key=get_sort_key, reverse=reverse)


class User:
    """Represents a user of the video game backlog application.

    This class manages user information, including username and the associated game backlog.

    Attributes:
        username (str): The username of the user.
        backlog (Backlog): The game backlog associated with the user.
    """

    def __init__(self, username: str):
        """Initialize a new user instance and load their backlog if it exists.

        Args:
            username (str): The username of the user.

        Raises:
            ValidationError: If the username is invalid or already exists.
        """
        self.username = username
        self.filename = f"{self.username}_backlog.json"
        self.backlog = Backlog(filename=self.filename)
        # Check if the backlog file already exists to load it; otherwise, create a new one
        if os.path.exists(self.filename):
            self.backlog.load_from_file(self.filename)
        else:
            self.save_backlog()  # Save the backlog when creating a new user

    def __str__(self) -> str:
        """Return a string representation of the user.

        Returns:
            str: A string that includes the username and the number of games in the backlog.
        """
        return f"User: {self.username}, Games in Backlog: {self.backlog.game_count()}"

    def __repr__(self) -> str:
        """Return a formal string representation of the user instance for debugging.

        Returns:
            str: A string representation of the User instance.
        """
        return f"User(username={self.username!r}, backlog={self.backlog!r})"

    @property
    def username(self) -> str:
        """Return the username of the user.

        Returns:
            str: The username of the user.
        """
        return self._username

    @username.setter
    def username(self, value: str):
        """Set the username for the user.

        Args:
            value (str): The new username for the user.

        Raises:
            ValidationError: If the username is empty, not a string, or already exists.
        """
        if not value or not isinstance(value, str):
            raise ValidationError("Username must be a non-empty string.")
        self._username = value

    @property
    def backlog(self) -> Backlog:
        """Return the backlog associated with the user.

        Returns:
            Backlog: The backlog of the user.
        """
        return self._backlog

    @backlog.setter
    def backlog(self, value: Backlog):
        """Set the backlog for the user.

        Args:
            value (Backlog): The backlog to be associated with the user.

        Raises:
            ValidationError: If the provided value is not an instance of Backlog.
        """
        if not isinstance(value, Backlog):
            raise ValidationError("Backlog must be an instance of the Backlog class.")
        self._backlog = value

    def save_backlog(self):
        """Save the user's backlog to a file."""
        # The filename is derived from the username, ensuring each user has a unique backlog file.
        filename = f"{self.username}_backlog.json"
        self.backlog.save_to_file(filename)

    def load_backlog(self):
        """Load the user's backlog from a file."""
        # Load the backlog from the file named after the user.
        filename = f"{self.username}_backlog.json"
        self.backlog.load_from_file(filename)

    @staticmethod
    def list_users():
        """Lists all existing users by scanning for user files."""
        # User files are identified by the '_backlog.json' suffix in the current directory.
        user_files = [f for f in os.listdir() if f.endswith("_backlog.json")]
        users = sorted(
            [os.path.splitext(file)[0].replace("_backlog", "") for file in user_files]
        )
        return users

    @staticmethod
    def delete_user(username):
        """Deletes a user's file.

        Args:
            username (str): The username of the user to be deleted.

        Returns:
            bool: True if the user was successfully deleted, False otherwise.
        """
        # Removes the file associated with the specified username.
        filename = f"{username}_backlog.json"
        if os.path.exists(filename):
            os.remove(filename)
            return True
        return False

    @staticmethod
    def switch_user(current_username):
        """Switches the active user."""
        users = User.list_users()
        if len(users) <= 1:
            print("No other users to switch to.")
            return None

        print("Existing users: " + ", ".join(users))
        new_username = input("Enter the username to switch to: ")
        if new_username == current_username:
            print("You are already logged in as this user.")
            return None
        elif new_username in users:
            return User(new_username)
        else:
            print("User not found.")
            return None


def create_new_user():
    """
    Create a new user profile.

    This function prompts the user to input a new username. If the username is valid and not already in use,
    it creates a new user profile and saves it to a file.

    Returns:
        User: The newly created user object, or None if creation failed.
    """
    while True:
        try:
            username = input("Enter a new username: ")
            if not username:
                raise ValidationError("Username cannot be empty.")
            filename = f"{username}_backlog.json"
            if os.path.exists(filename):
                print("Username already exists. Please try a different username.")
                continue
            print(f"New user profile created for {username}.")
            return User(username)
        except ValidationError as e:
            print(e)


def load_existing_user():
    """
    Load an existing user profile.

    Prompts the user to input their username, and attempts to load the corresponding user profile from a file.
    If the profile exists and is successfully loaded, the user object is returned.

    Returns:
        User: The loaded user object, or None if loading failed.
    """
    users = User.list_users()
    if users:
        print("Existing users: " + ", ".join(users))
    else:
        print("No users available to load.")
        return None
    username = input("Enter name of user to load: ")
    filename = f"{username}_backlog.json"
    if not os.path.exists(filename):
        print("User profile not found. Please try again or create a new user.")
        return None
    else:
        user = User(username)
        try:
            user.load_backlog()
            print(f"Welcome back, {user.username}!")
            return user
        except FileIOError as e:
            print(f"Error loading user profile: {e}")
            return None


def manage_backlog(user):
    """
    Manage the game backlog for a user.

    Presents a menu of options to the user for managing their game backlog, including adding or removing games,
    sorting the backlog, and more. This function forms the core of the user's interaction with their backlog.

    Args:
        user (User): The user whose backlog is being managed.
    """
    # Main menu loop for backlog management
    while True:
        print("\n--- Main Menu ---")
        print("1. Add a game to the backlog")
        print("2. Remove a game from the backlog")
        print("3. Sort and show all games in the backlog")
        print("4. List existing users")
        print("5. Delete a user")
        print("6. Switch user")
        print("7. Exit")
        choice = input("Enter your choice: ")

        # Each 'if' block corresponds to a different menu option
        if choice == "1":
            # Add a game to the backlog
            title = mandatory_string_input("Enter game title: ")
            genre = optional_string_input("Enter game genre (or leave blank): ")
            release_year = optional_int_input(
                "Enter release year (or leave blank): ", min_value=1950
            )
            date_added = date.today()
            time_to_beat = optional_time_input(
                "Enter time to beat as HH:MM (or leave blank): "
            )
            priority = optional_int_input(
                "Enter priority (or leave blank): ", min_value=0
            )
            game = Game(
                title,
                genre,
                release_year,
                date_added,
                time_to_beat,
                priority,
            )
            user.backlog.add_game(game)
            print(f"'{title}' added to your backlog.")

        elif choice == "2":
            # Remove a game from the backlog
            if user.backlog.game_count() == 0:
                print("Your backlog is empty.")
            else:
                title = input("Enter the title of the game to remove: ")
                game_to_remove = None
                for game in user.backlog.games:
                    if game.title.lower() == title.lower():
                        game_to_remove = game
                        break

                if game_to_remove:
                    user.backlog.remove_game(game_to_remove)
                    print(f"Game '{title}' removed from your backlog.")
                else:
                    print("Game not found in backlog.")

        elif choice == "3":
            # Display and sort all games in the backlog
            if user.backlog.game_count() == 0:
                print("Your backlog is empty.")
            else:
                # Choose sorting criterion
                print("\nSort by:")
                print("1. Title")
                print("2. Genre")
                print("3. Release Year")
                print("4. Priority")
                print("5. Time to Beat")
                print("6. Date Added")
                sort_choice = input("Enter your choice for sorting: ")
                sort_criterion = {
                    "1": "title",
                    "2": "genre",
                    "3": "release_year",
                    "4": "priority",
                    "5": "time_to_beat",
                    "6": "date_added",
                }.get(
                    sort_choice, "title"
                )  # default to title if invalid choice

                # Sort and display games
                user.backlog.sort_backlog(criterion=sort_criterion)
                print("\nGames in your backlog:")
                for game in user.backlog.games:
                    time_to_beat_str = (
                        f"{game.time_to_beat[0]}h{game.time_to_beat[1]}m"
                        if game.time_to_beat is not None
                        else "N/A"
                    )
                    print(
                        f"- {game.title} (Genre: {game.genre}, Release Year: {game.release_year}, Time to Beat: {time_to_beat_str}, Priority: {game.priority}, Date Added: {game.date_added})"
                    )

        elif choice == "4":
            # List all existing users
            users = User.list_users()
            print("Existing users: " + ", ".join(users))

        elif choice == "5":
            # Delete a user
            users = User.list_users()
            if users:
                print("Existing users: " + ", ".join(users))
                username_to_delete = input("Enter the username of the user to delete: ")

                if username_to_delete in users:
                    user_deleted = User.delete_user(username_to_delete)
                    if user_deleted:
                        print(f"User {username_to_delete}'s profile deleted.")
                        if user and user.username == username_to_delete:
                            print(
                                "You have deleted your active profile. Returning to the main screen."
                            )
                            return True, None
                    else:
                        print("Error: Could not delete the user profile.")
                else:
                    print("User not found.")
            else:
                print("No users available to delete.")

        elif choice == "6":
            # Switch to a different user
            switched_user = User.switch_user(user.username)
            if switched_user:
                user = switched_user
                print(f"Switched to user {user.username}")

        elif choice == "7":
            # Exit the application
            print("Goodbye!")
            return False, user

        else:
            print("Invalid choice, please try again.")


def optional_int_input(prompt, min_value=None):
    """
    Prompt for an optional integer input.

    Allows the user to input an integer or skip the input. If an integer is provided,
    it validates that the integer is greater than or equal to a specified minimum value, if provided.

    Args:
        prompt (str): The prompt message to display to the user.
        min_value (int, optional): The minimum acceptable value for the integer input.

    Returns:
        int or None: The integer input by the user, or None if the user skips the input.
    """
    while True:
        input_str = input(prompt)
        if input_str == "":
            return None
        if input_str.isdigit():
            value = int(input_str)
            if min_value is not None and value < min_value:
                print(f"Please enter a number greater than or equal to {min_value}.")
                continue
            return value
        else:
            print("Invalid input. Please enter a valid integer or leave blank.")
            continue


def optional_string_input(prompt):
    """
    Prompt for an optional string input.

    Allows the user to input a string or skip the input by providing an empty string.

    Args:
        prompt (str): The prompt message to display to the user.

    Returns:
        str or None: The string input by the user, or None if the user skips the input.
    """
    return input(prompt).strip() or None


def optional_time_input(prompt):
    """
    Prompt for a time input in HH:MM format with an option to skip.

    Allows the user to input a time value in hours and minutes or skip the input. Validates the format
    and values to ensure they represent a valid time.

    Args:
        prompt (str): The prompt message to display to the user.

    Returns:
        tuple of (int, int) or None: A tuple representing hours and minutes, or None if the user skips the input.
    """
    while True:
        input_str = input(prompt)
        if input_str == "":
            return None
        parts = input_str.split(":")
        if len(parts) != 2:
            print("Invalid format. Please enter a valid time (HH:MM) or leave blank.")
            continue
        try:
            hours, minutes = map(int, parts)
            if hours < 0 or minutes < 0 or minutes >= 60:
                print(
                    "Invalid input. Please enter a valid time (HH:MM) or leave blank."
                )
                continue
            return (hours, minutes)
        except ValueError:
            print("Invalid input. Please enter a valid time (HH:MM) or leave blank.")


def mandatory_string_input(prompt):
    """
    Prompt for a mandatory string input.

    Requires the user to input a non-empty string. Continues to prompt until a valid input is received.

    Args:
        prompt (str): The prompt message to display to the user.

    Returns:
        str: The non-empty string input by the user.
    """
    while True:
        input_str = input(prompt).strip()
        if input_str:
            return input_str
        print("This field is required. Please enter a value.")


if __name__ == "__main__":
    main()
