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

TEAM_1_COLOR = 0x00AA00
TEAM_2_COLOR = 0xAAAAAA

# Red Score
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(4, int(matrixportal.graphics.display.height * 0.75) - 3),
    text_color=TEAM_1_COLOR,
    text_scale=2,
)

# Blue Score
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(36, int(matrixportal.graphics.display.height * 0.75) - 3),
    text_color=TEAM_2_COLOR,
    text_scale=2,
)

# Red Team name
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(4, int(matrixportal.graphics.display.height * 0.25) - 4),
    text_color=TEAM_1_COLOR,
)

# Blue Team name
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(36, int(matrixportal.graphics.display.height * 0.25) - 4),
    text_color=TEAM_2_COLOR,
)

# Static 'Connecting' Text
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(59, 0),
)

SCORES_1_FEED = "homeassistant/findeiss/1/dispenses/today"
SCORES_2_FEED = "homeassistant/findeiss/1/dispenses/yesterday"
TEAM_1_FEED = "homeassistant/findeiss/1/dispenses/today/label"
TEAM_2_FEED = "homeassistant/findeiss/1/dispenses/yesterday/label"
TEAM_1_COLOR_FEED = "homeassistant/findeiss/1/dispenses/today/color"
TEAM_2_COLOR_FEED = "homeassistant/findeiss/1/dispenses/yesterday/color"

last_data = {}

UPDATE_DELAY = 4

matrixportal.set_text_color(TEAM_1_COLOR, 0)
matrixportal.set_text_color(TEAM_2_COLOR, 1)


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
    team_1 = "Red"
    team_2 = "Blue"

    global TEAM_1_COLOR
    global TEAM_2_COLOR

    show_connecting(True)
    team_name = get_last_data(TEAM_1_FEED)
    if team_name is not None:
        print("Team {} is now Team {}".format(team_1, team_name))
        team_1 = team_name
    matrixportal.set_text(team_1, 2)
    team_color = get_last_data(TEAM_1_COLOR_FEED)
    if team_color is not None:
        team_color = int(team_color.replace("#", "").strip(), 16)
        print("Team {} is now Team {}".format(team_1, team_color))
        TEAM_1_COLOR = team_color
    matrixportal.set_text_color(TEAM_1_COLOR, 2)
    matrixportal.set_text_color(TEAM_1_COLOR, 0)
    team_name = get_last_data(TEAM_2_FEED)
    if team_name is not None:
        print("Team {} is now Team {}".format(team_2, team_name))
        team_2 = team_name
    matrixportal.set_text(team_2, 3)
    team_color = get_last_data(TEAM_2_COLOR_FEED)
    if team_color is not None:
        team_color = int(team_color.replace("#", "").strip(), 16)
        print("Team {} is now Team {}".format(team_2, team_color))
        TEAM_2_COLOR = team_color
    matrixportal.set_text_color(TEAM_2_COLOR, 3)
    matrixportal.set_text_color(TEAM_2_COLOR, 1)
    show_connecting(False)


def update_scores():
    print("Updating data from Adafruit IO")
    show_connecting(True)

    score_red = get_last_data(SCORES_1_FEED)
    if score_red is None:
        score_red = 0
    matrixportal.set_text(score_red, 0)

    score_blue = get_last_data(SCORES_2_FEED)
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
    mqtt.subscribe(SCORES_2_FEED)
    mqtt.subscribe(SCORES_1_FEED)
    mqtt.subscribe(TEAM_2_FEED)
    mqtt.subscribe(TEAM_1_FEED)
    mqtt.subscribe(TEAM_2_COLOR_FEED)
    mqtt.subscribe(TEAM_1_COLOR_FEED)


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