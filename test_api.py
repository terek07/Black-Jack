"""
Integration tests for the Blackjack Web API
"""
import pytest
import requests
import time

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module", autouse=True)
def wait_for_server():
    """Wait for the server to be ready"""
    max_attempts = 10
    for _ in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                return
        except requests.exceptions.RequestException:
            time.sleep(1)
    pytest.skip("Backend server not available")


def test_health_check():
    """Test the health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_start_game_single_player():
    """Test starting a game with one player"""
    payload = {
        "players": [
            {"name": "Alice", "bet": 100}
        ]
    }
    response = requests.post(f"{BASE_URL}/api/game/start", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "game_id" in data
    assert len(data["players"]) == 1
    assert data["players"][0]["name"] == "Alice"
    assert data["players"][0]["balance"] == 1000
    assert len(data["players"][0]["hands"]) == 1
    assert data["players"][0]["hands"][0]["bet"] == 100
    assert len(data["dealer_hand"]) == 1  # Only showing one card


def test_start_game_multiple_players():
    """Test starting a game with multiple players"""
    payload = {
        "players": [
            {"name": "Alice", "bet": 100},
            {"name": "Bob", "bet": 50},
            {"name": "Charlie", "bet": 75}
        ]
    }
    response = requests.post(f"{BASE_URL}/api/game/start", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["players"]) == 3
    assert data["players"][0]["name"] == "Alice"
    assert data["players"][1]["name"] == "Bob"
    assert data["players"][2]["name"] == "Charlie"


def test_player_actions():
    """Test hit and stand actions"""
    # Start a game
    payload = {"players": [{"name": "TestPlayer", "bet": 100}]}
    response = requests.post(f"{BASE_URL}/api/game/start", json=payload)
    game_data = response.json()
    game_id = game_data["game_id"]
    
    # Test hit
    hit_payload = {
        "game_id": game_id,
        "player_index": 0,
        "hand_index": 0
    }
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/hit", json=hit_payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["players"][0]["hands"][0]["cards"]) == 3
    
    # Test stand
    stand_payload = {
        "game_id": game_id,
        "player_index": 0,
        "hand_index": 0
    }
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/stand", json=stand_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["players"][0]["hands"][0]["is_finished"] is True


def test_game_not_found():
    """Test accessing non-existent game"""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = requests.get(f"{BASE_URL}/api/game/{fake_id}")
    assert response.status_code == 404


def test_complete_game_flow():
    """Test a complete game from start to finish"""
    # Start game
    payload = {"players": [{"name": "Player1", "bet": 100}]}
    response = requests.post(f"{BASE_URL}/api/game/start", json=payload)
    assert response.status_code == 200
    game_data = response.json()
    game_id = game_data["game_id"]
    
    # Player stands
    stand_payload = {
        "game_id": game_id,
        "player_index": 0,
        "hand_index": 0
    }
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/stand", json=stand_payload)
    assert response.status_code == 200
    
    # Resolve game
    response = requests.post(f"{BASE_URL}/api/game/{game_id}/resolve")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["dealer_hand"]) >= 2  # Dealer cards now visible


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
