# Matrix Portal Scoreboard with CircuitPython

## Description

This project is a scoreboard that reads values over MQTT from a local broker. 
It uses the 64x32 pixel RGB matrix and MatrixPortal board from Adafruit. 
In my classroom, I have it reading values from a local MQTT broker that is
connected to Home Assistant. 

Values are updated in near-realtime and it is encouraged to publish all values
using the retain flag so that the scoreboard will retrieve the latest values when
it reboots.

## Equipment

- [Adafruit Matrix Portal - CircuitPython Powered Internet Display](https://www.adafruit.com/product/4745)
- [64x32 RGB LED Matrix - 5mm pitch](https://www.adafruit.com/product/2277)

## MQTT Values

- Team Names
- Scores

## Useful Guides

- [MatrixPortal M4 Learning Guide](https://learn.adafruit.com/adafruit-matrixportal-m4/overview
- [Adafruit MiniMQTT Library](https://circuitpython.readthedocs.io/projects/minimqtt/en/latest/)
- [Matrix Portal Scoreboard](https://learn.adafruit.com/matrix-portal-scoreboard)

