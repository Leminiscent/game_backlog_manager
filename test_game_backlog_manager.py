import pytest
from game_backlog_manager import (
    Game,
    Backlog,
    User,
    ValidationError,
    InvalidGameDataError,
    FileIOError,
    InvalidDateError,
    DuplicateUsernameError,
    create_new_user,
    load_existing_user,
    manage_backlog,
    optional_int_input,
    optional_string_input,
    optional_time_input,
    mandatory_string_input,
)
from datetime import date
import os
from unittest.mock import patch

# Sample data for testing
valid_game_data = {
    "title": "Test Game",
    "genre": "Adventure",
    "release_year": 2020,
    "date_added": date.today(),
    "time_to_beat": (10, 30),
    "priority": 1,
}

invalid_game_data = {
    "title": "",
    "genre": 123,  # Invalid: genre should be a string
    "release_year": -2020,  # Invalid: release year should be positive
    "time_to_beat": (10, -30),  # Invalid: negative minutes
}


# Game Class Tests
def test_game_creation_valid():
    game = Game(**valid_game_data)
    assert game.title == valid_game_data["title"]
    assert game.genre == valid_game_data["genre"]
    assert game.release_year == valid_game_data["release_year"]
    assert game.date_added == valid_game_data["date_added"]
    assert game.time_to_beat == valid_game_data["time_to_beat"]
    assert game.priority == valid_game_data["priority"]


def test_game_creation_invalid():
    with pytest.raises(InvalidGameDataError):
        Game(**invalid_game_data)


# Backlog Class Tests
def test_backlog_add_game():
    backlog = Backlog("test_backlog.json")
    game = Game(**valid_game_data)
    backlog.add_game(game)
    assert game in backlog.games
    assert len(backlog.games) == 1


def test_backlog_remove_game():
    backlog = Backlog("test_backlog.json")
    game = Game(**valid_game_data)
    backlog.add_game(game)
    backlog.remove_game(game)
    assert game not in backlog.games


def test_backlog_save_load():
    backlog = Backlog("test_backlog.json")
    game = Game(**valid_game_data)
    backlog.add_game(game)
    backlog.save_to_file("test_backlog.json")
    backlog.load_from_file("test_backlog.json")
    assert game in backlog.games


def test_sort_backlog():
    backlog = Backlog("test_backlog.json")
    game1 = Game(title="Game A", release_year=2020)
    game2 = Game(title="Game B", release_year=2021)
    backlog.add_game(game1)
    backlog.add_game(game2)
    backlog.sort_backlog("release_year")
    assert backlog.games[0].title == "Game A"
    backlog.sort_backlog("release_year", reverse=True)
    assert backlog.games[0].title == "Game B"


# User Class Tests
def test_user_creation_and_load():
    user = User("test_user")
    user.save_backlog()
    loaded_user = User("test_user")
    loaded_user.load_backlog()
    assert loaded_user.username == "test_user"


def test_user_backlog_operations():
    user = User("test_user")
    game = Game(**valid_game_data)
    user.backlog.add_game(game)
    assert game in user.backlog.games


# Integration Tests
def test_full_flow():
    user = User("test_user")
    game = Game(**valid_game_data)
    user.backlog.add_game(game)
    assert game in user.backlog.games
    user.save_backlog()
    user.load_backlog()
    assert game in user.backlog.games
    user.backlog.remove_game(game)
    assert game not in user.backlog.games


# Test utility functions
def test_optional_int_input():
    with patch("builtins.input", return_value="10"):
        assert optional_int_input("Enter a number: ") == 10


def test_optional_string_input():
    with patch("builtins.input", return_value="test"):
        assert optional_string_input("Enter a string: ") == "test"


def test_optional_time_input():
    with patch("builtins.input", return_value="10:30"):
        assert optional_time_input("Enter time: ") == (10, 30)


def test_mandatory_string_input():
    with patch("builtins.input", return_value="mandatory"):
        assert mandatory_string_input("Enter a string: ") == "mandatory"


# Test create_new_user and load_existing_user functions
def test_create_and_load_user():
    with patch("builtins.input", return_value="new_user"):
        new_user = create_new_user()
        assert new_user.username == "new_user"

    loaded_user = load_existing_user()
    assert loaded_user.username == new_user.username


# Test manage_backlog function
def test_manage_backlog():
    user = User("test_user")
    game = Game(**valid_game_data)
    user.backlog.add_game(game)

    # Mock user input for managing backlog
    with patch("builtins.input", side_effect=["1", "Game Title", "exit"]):
        manage_backlog(user)
        assert "Game Title" in [game.title for game in user.backlog.games]


# Cleanup
def teardown_module(module):
    if os.path.exists("test_backlog.json"):
        os.remove("test_backlog.json")
    if os.path.exists("test_user_backlog.json"):
        os.remove("test_user_backlog.json")
