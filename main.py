import argparse
import json
import mimetypes
from pathlib import Path
import random
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


CHOICES = ["rock", "paper", "scissors", "lizard", "spock"]
WINNING_RULES = {
	"rock": {"scissors", "lizard"},
	"paper": {"rock", "spock"},
	"scissors": {"paper", "lizard"},
	"lizard": {"paper", "spock"},
	"spock": {"rock", "scissors"},
}


def normalize_choice(value):
	if value is None:
		return None
	normalized = str(value).strip().lower()
	return normalized if normalized in CHOICES else None


def get_computer_choice():
	return random.choice(CHOICES)


def get_winner(player_choice, computer_choice):
	player_choice = normalize_choice(player_choice)
	computer_choice = normalize_choice(computer_choice)

	if not player_choice or not computer_choice:
		raise ValueError("Invalid choice. Valid options are: rock, paper, scissors, lizard, spock")

	if player_choice == computer_choice:
		return "tie"

	if computer_choice in WINNING_RULES[player_choice]:
		return "player"

	return "computer"


def build_round_result(player_choice, computer_choice):
	winner = get_winner(player_choice, computer_choice)
	messages = {
		"player": "You win!",
		"computer": "Computer wins!",
		"tie": "It's a tie!",
	}
	return {
		"player_choice": player_choice,
		"computer_choice": computer_choice,
		"winner": winner,
		"message": messages[winner],
	}


def play_round(player_choice):
	normalized_choice = normalize_choice(player_choice)
	if not normalized_choice:
		raise ValueError("Invalid choice. Choose one of: rock, paper, scissors, lizard, spock")

	computer_choice = get_computer_choice()
	return build_round_result(normalized_choice, computer_choice)


def prompt_player_choice():
	print("Choose your option:")
	for idx, choice in enumerate(CHOICES, start=1):
		print(f"{idx}. {choice.capitalize()}")

	user_input = input("Enter number (1-5) or name: ").strip().lower()

	if user_input.isdigit():
		option = int(user_input)
		if 1 <= option <= len(CHOICES):
			return CHOICES[option - 1]

	return normalize_choice(user_input)


def extract_player_choice(path, payload):
	parsed_path = urlparse(path).path.strip("/")
	if parsed_path.startswith("api/"):
		parsed_path = parsed_path[4:]

	route_choice = normalize_choice(parsed_path)
	if route_choice:
		return route_choice

	if isinstance(payload, dict):
		return normalize_choice(payload.get("choice") or payload.get("player_choice"))

	return None


class GameRequestHandler(BaseHTTPRequestHandler):
	BASE_DIR = Path(__file__).resolve().parent
	UI_DIR = BASE_DIR / "ui"

	def _send_json(self, status_code, body):
		data = json.dumps(body).encode("utf-8")
		self._send_bytes(status_code, "application/json", data)

	def _send_bytes(self, status_code, content_type, data):
		self.send_response(status_code)
		self.send_header("Content-Type", content_type)
		self.send_header("Content-Length", str(len(data)))
		self.end_headers()
		self.wfile.write(data)

	def _serve_static_file(self, relative_path):
		file_path = (self.UI_DIR / relative_path).resolve()
		if not str(file_path).startswith(str(self.UI_DIR.resolve())):
			self._send_json(403, {"error": "Forbidden"})
			return

		if not file_path.exists() or not file_path.is_file():
			self._send_json(404, {"error": "Not Found"})
			return

		content = file_path.read_bytes()
		content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
		self._send_bytes(200, content_type, content)

	def do_GET(self):
		path = urlparse(self.path).path

		if path in {"/", "/ui", "/ui/"}:
			self._serve_static_file("index.html")
			return

		if path == "/ui/styles.css":
			self._serve_static_file("styles.css")
			return

		if path == "/ui/app.js":
			self._serve_static_file("app.js")
			return

		if path in {"/api", "/api/"}:
			self._send_json(
				200,
				{
					"message": "Rock Paper Scissors Lizard Spock API",
					"usage": {
						"post_payload": "POST /api/play with JSON {\"choice\": \"rock\"}",
						"post_route": "POST /api/rock (or /paper, /scissors, /lizard, /spock)",
					},
				},
			)
			return

		self._send_json(404, {"error": "Not Found"})

	def do_POST(self):
		path = urlparse(self.path).path
		length = int(self.headers.get("Content-Length", "0"))
		raw = self.rfile.read(length) if length > 0 else b""

		payload = {}
		if raw:
			try:
				payload = json.loads(raw.decode("utf-8"))
			except json.JSONDecodeError:
				self._send_json(400, {"error": "Invalid JSON payload"})
				return

		player_choice = extract_player_choice(path, payload)
		if not player_choice:
			self._send_json(
				400,
				{
					"error": "Invalid or missing choice",
					"valid_choices": CHOICES,
					"examples": ["POST /rock", "POST /play with JSON {\"choice\":\"rock\"}"],
				},
			)
			return

		result = play_round(player_choice)
		self._send_json(200, result)


def run_cli():
	print("Welcome to Rock, Paper, Scissors, Lizard, Spock!")
	player_choice = prompt_player_choice()

	if not player_choice:
		print("Invalid choice. Please choose a number from 1-5 or a valid name.")
		return

	result = play_round(player_choice)
	print(f"You chose: {result['player_choice']}")
	print(f"Computer chose: {result['computer_choice']}")
	print(result["message"])


def run_api(host, port):
	server = HTTPServer((host, port), GameRequestHandler)
	print(f"Starting API server on http://{host}:{port}")
	print("Try POST /rock or POST /play with JSON {'choice':'rock'}")
	server.serve_forever()


def main():
	parser = argparse.ArgumentParser(description="Rock Paper Scissors Lizard Spock")
	parser.add_argument("--api", action="store_true", help="Run as REST API server")
	parser.add_argument("--host", default="127.0.0.1", help="API host (default: 127.0.0.1)")
	parser.add_argument("--port", type=int, default=8000, help="API port (default: 8000)")
	args = parser.parse_args()

	if args.api:
		run_api(args.host, args.port)
	else:
		run_cli()


if __name__ == "__main__":
	main()
