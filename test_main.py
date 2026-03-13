import pytest

from main import CHOICES, WINNING_RULES, extract_player_choice, get_winner, normalize_choice


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("rock", "rock"),
        (" ROCK ", "rock"),
        ("Spock", "spock"),
        ("lizard", "lizard"),
        ("", None),
        ("banana", None),
        (None, None),
    ],
)
def test_normalize_choice(raw, expected):
    assert normalize_choice(raw) == expected


@pytest.mark.parametrize("player", CHOICES)
@pytest.mark.parametrize("computer", CHOICES)
def test_get_winner_all_combinations(player, computer):
    result = get_winner(player, computer)

    if player == computer:
        assert result == "tie"
    elif computer in WINNING_RULES[player]:
        assert result == "player"
    else:
        assert result == "computer"


def test_get_winner_rejects_invalid_player_choice():
    with pytest.raises(ValueError):
        get_winner("invalid", "rock")


def test_get_winner_rejects_invalid_computer_choice():
    with pytest.raises(ValueError):
        get_winner("rock", "invalid")


def test_extract_player_choice_from_route():
    assert extract_player_choice("/rock", {}) == "rock"
    assert extract_player_choice("/Spock", {}) == "spock"


def test_extract_player_choice_from_payload_choice_key():
    payload = {"choice": "paper"}
    assert extract_player_choice("/play", payload) == "paper"


def test_extract_player_choice_from_payload_player_choice_key():
    payload = {"player_choice": "lizard"}
    assert extract_player_choice("/play", payload) == "lizard"


def test_extract_player_choice_returns_none_when_missing_or_invalid():
    assert extract_player_choice("/play", {}) is None
    assert extract_player_choice("/play", {"choice": "banana"}) is None
