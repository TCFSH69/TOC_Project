import os

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, LocationMessage

from utils import send_text_message
from machine import create_machine
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__, static_url_path="")


# Get channel_secret and channel_access_token from environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

# Unique FSM for each user
machines = {}

def event_processing(uid, event):
	response = machines[event.source.user_id].advance(event)
	if response == False:
		send_text_message(event.reply_token, "Invalid command, try again")

def return_to_menu(uid, event):
	send_text_message(event.reply_token, "已回到主選單")
	machines[event.source.user_id].go_to_menu(event)

# Simple callback endpoint for testing connection
@app.route("/callback", methods=["POST"])
def callback():
	signature = request.headers["X-Line-Signature"]
	# get request body as text
	body = request.get_data(as_text=True)

	# parse webhook body
	try:
		events = parser.parse(body, signature)
	except InvalidSignatureError:
		abort(400)

	# if event is MessageEvent and message is TextMessage, then echo text
	for event in events:
		if not isinstance(event, MessageEvent):
			continue
		if not isinstance(event.message, TextMessage):
			continue

		line_bot_api.reply_message(
			event.reply_token, TextSendMessage(text=event.message.text)
		)

	return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
	signature = request.headers["X-Line-Signature"]
	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info(f"Request body: {body}")

	# parse webhook body
	try:
		events = parser.parse(body, signature)
	except InvalidSignatureError:
		abort(400)

	for event in events:
		# Create a machine for new user
		if event.source.user_id not in machines:
			machines[event.source.user_id] = create_machine()

		print(event)

		if not isinstance(event, MessageEvent):
			continue

		if isinstance(event.message, TextMessage):
			if event.message.text == "go to menu":
				return_to_menu(event.source.user_id, event)
			else:
				event_processing(event.source.user_id, event)
		else:
			if machines[event.source.user_id].state in ["set_current_location"]:
				event_processing(event.source.user_id, event)
			else:
				send_text_message(event.reply_token, "Invalid command, try again")

		print(f"\nFSM STATE: {machines[event.source.user_id].state}")

	return "OK"


if __name__ == "__main__":
	port = os.environ.get("PORT", 8000)
	app.run(host="0.0.0.0", port=port)