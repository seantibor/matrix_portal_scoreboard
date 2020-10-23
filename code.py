# Scoreboard matrix display
# uses AdafruitIO to set scores and team names for a scoreboard
# Perfect for cornhole, ping pong, and other games

import time
import board
import terminalio
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_matrixportal.network import Network
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from secrets import secrets

# --- Display setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=False)
network = matrixportal.network
network.connect()

mqtt = MQTT.MQTT(
    broker=secrets.get("mqtt_broker"),
    username=secrets.get("mqtt_user"),
    password=secrets.get("mqtt_password"),
    port=1883,
)

MQTT.set_socket(socket, network._wifi.esp)

RED_COLOR = 0x00AA00
BLUE_COLOR = 0xAAAAAA

# Red Score
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(4, int(matrixportal.graphics.display.height * 0.75) - 3),
    text_color=RED_COLOR,
    text_scale=2,
)

# Blue Score
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(36, int(matrixportal.graphics.display.height * 0.75) - 3),
    text_color=BLUE_COLOR,
    text_scale=2,
)

# Red Team name
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(4, int(matrixportal.graphics.display.height * 0.25) - 4),
    text_color=RED_COLOR,
)

# Blue Team name
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(36, int(matrixportal.graphics.display.height * 0.25) - 4),
    text_color=BLUE_COLOR,
)

# Static 'Connecting' Text
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(59, 0),
)

SCORES_RED_FEED = "homeassistant/findeiss/1/dispenses/today"
SCORES_BLUE_FEED = "homeassistant/findeiss/1/dispenses/yesterday"
TEAM_RED_FEED = "homeassistant/findeiss/1/dispenses/today/label"
TEAM_BLUE_FEED = "homeassistant/findeiss/1/dispenses/yesterday/label"

last_data = {}

UPDATE_DELAY = 4

matrixportal.set_text_color(RED_COLOR, 0)
matrixportal.set_text_color(BLUE_COLOR, 1)


def show_connecting(show):
    if show:
        matrixportal.set_text(".", 4)
    else:
        matrixportal.set_text(" ", 4)


def message_received(client, topic, message):
    print("Received {} for {}".format(message, topic))
    last_data[topic] = message
    update_scores()
    customize_team_names()


def get_last_data(feed):
    return last_data.get(feed)


def customize_team_names():
    team_red = "Red"
    team_blue = "Blue"

    show_connecting(True)
    team_name = get_last_data(TEAM_RED_FEED)
    if team_name is not None:
        print("Team {} is now Team {}".format(team_red, team_name))
        team_red = team_name
    matrixportal.set_text(team_red, 2)
    team_name = get_last_data(TEAM_BLUE_FEED)
    if team_name is not None:
        print("Team {} is now Team {}".format(team_blue, team_name))
        team_blue = team_name
    matrixportal.set_text(team_blue, 3)
    show_connecting(False)


def update_scores():
    print("Updating data from Adafruit IO")
    show_connecting(True)

    score_red = get_last_data(SCORES_RED_FEED)
    if score_red is None:
        score_red = 0
    matrixportal.set_text(score_red, 0)

    score_blue = get_last_data(SCORES_BLUE_FEED)
    if score_blue is None:
        score_blue = 0
    matrixportal.set_text(score_blue, 1)
    show_connecting(False)


def subscribe():
    try:
        mqtt.is_connected()
    except MQTT.MMQTTException:
        mqtt.connect()
    mqtt.on_message = message_received
    mqtt.subscribe(SCORES_BLUE_FEED)
    mqtt.subscribe(SCORES_RED_FEED)
    mqtt.subscribe(TEAM_BLUE_FEED)
    mqtt.subscribe(TEAM_RED_FEED)


subscribe()
customize_team_names()
update_scores()
last_update = time.monotonic()

while True:
    # Set the red score text
    try:
        mqtt.is_connected()
    except MQTT.MMQTTException:
        mqtt.reconnect()
    mqtt.loop()