# Game Backlog Manager

The Game Backlog Manager is a Python application designed to help users manage their collection of video games. It offers a range of functionalities including the ability to add, remove, sort, and display games in the backlog, as well as manage user profiles. This document serves as a guide to understand and use the application effectively.

## Features

- **User Management**: Create new user profiles, load existing profiles, and switch between users.
- **Backlog Management**: Add and remove games from your backlog, with attributes like title, genre, release year, and more.
- **Game Sorting**: Sort games in your backlog based on various criteria like title, genre, release year, etc.
- **Data Persistence**: Save and load your game backlog to and from files, ensuring data is stored between sessions.

## Classes

- `Game`: Represents a single video game, including attributes like title, genre, release year, date added, time to beat, and priority.
- `Backlog`: Manages a collection of games for a user, with functionalities to add, remove, and sort games, as well as save and load from files.
- `User`: Represents a user of the application, managing their game backlog.

## Exceptions

- `ValidationError`: Base class for exceptions related to validation errors.
- `InvalidGameDataError`: Raised for errors in game data structure or content.
- `FileIOError`: Raised for errors during file I/O operations.
- `InvalidDateError`: Raised for errors related to date format or value.
- `DuplicateUsernameError`: Raised when a duplicate username is encountered.

## Main Functionality

The application's primary interface is handled through the `main()` function. This function facilitates user interaction with the application, allowing them to perform actions like creating or loading user profiles and managing their game backlog. The application runs in a continuous loop, providing a menu-driven interface for easy navigation.

## Usage

To use the Game Backlog Manager:

1. Start the application. The main menu will be displayed.
2. Choose to create a new user, load an existing user, or exit the program.
3. Once a user profile is active, various options to manage the game backlog will be available:
    - Add a game
    - Remove a game
    - Sort and display all games
    - Additional user management options like listing existing users, deleting a user, or switching users
4. The application will continue running until you choose to exit.
