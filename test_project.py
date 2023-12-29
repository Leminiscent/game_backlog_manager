from datetime import date
from project import (
    Game,
    Backlog,
    User,
    InvalidGameDataError,
    FileIOError,
    InvalidDateError,
    ValidationError,
    DuplicateUsernameError,
)
import pytest


# Test cases for the Game class
class TestGame:
    def test_create_game_success(self):
        game = Game(title="Test Game", genre="RPG", release_year=2020, priority=1)
        assert game.title == "Test Game"
        assert game.genre == "RPG"
        assert game.release_year == 2020
        assert game.priority == 1

    def test_create_game_invalid_data(self):
        with pytest.raises(InvalidGameDataError):
            Game(title="", genre="RPG", release_year=2020)

    def test_create_game_invalid_date(self):
        with pytest.raises(InvalidDateError):
            Game(
                title="Test Game",
                genre="RPG",
                release_year=2020,
                date_added=date(2050, 1, 1),
            )


# Test cases for the Backlog class
class TestBacklog:
    def test_add_game(self):
        backlog = Backlog(filename="test_backlog.json")
        game = Game(title="Test Game", genre="RPG", release_year=2020)
        backlog.add_game(game)
        assert len(backlog.games) == 1
        assert backlog.games[0].title == "Test Game"

    def test_remove_game(self):
        backlog = Backlog(filename="test_backlog.json")
        game = Game(title="Test Game", genre="RPG", release_year=2020)
        backlog.add_game(game)
        backlog.remove_game(game)
        assert len(backlog.games) == 0

    def test_save_load_backlog(self):
        backlog = Backlog(filename="test_backlog.json")
        game = Game(title="Test Game", genre="RPG", release_year=2020)
        backlog.add_game(game)
        backlog.save_to_file("test_backlog.json")

        new_backlog = Backlog(filename="test_backlog.json")
        new_backlog.load_from_file("test_backlog.json")
        assert len(new_backlog.games) == 1
        assert new_backlog.games[0].title == "Test Game"

    def test_sort_backlog(self):
        backlog = Backlog(filename="test_backlog.json")
        game1 = Game(title="Z Game", genre="Action", release_year=2021)
        game2 = Game(title="A Game", genre="Adventure", release_year=2019)
        backlog.add_game(game1)
        backlog.add_game(game2)

        backlog.sort_backlog("title")
        assert backlog.games[0].title == "A Game"
        assert backlog.games[1].title == "Z Game"


# Test cases for the User class
class TestUser:
    def test_create_user(self):
        user = User("testuser")
        assert user.username == "testuser"
        assert isinstance(user.backlog, Backlog)

    def test_load_user(self):
        user = User("testuser")
        user.backlog.add_game(Game(title="Test Game", genre="RPG", release_year=2020))
        user.save_backlog()

        loaded_user = User("testuser")
        loaded_user.load_backlog()
        assert loaded_user.username == "testuser"
        assert len(loaded_user.backlog.games) == 1

    def test_delete_user(self):
        User("testuser2").save_backlog()
        assert User.delete_user("testuser2") is True

    def test_switch_user(self):
        User("testuser1").save_backlog()
        User("testuser3").save_backlog()
        current_user = User("testuser1")
        switched_user = User.switch_user(current_user.username)
        assert switched_user is not None
        assert switched_user.username != "testuser1"
