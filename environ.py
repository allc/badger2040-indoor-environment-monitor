import time
import badger2040
from breakout_bme68x import BreakoutBME68X, STATUS_HEATER_STABLE
from pimoroni_i2c import PimoroniI2C
import urequests
import sys
import ntptime

API = "https://io.adafruit.com/api/v2/{username}/groups/{group_key}/data"
API_KEY = ""

badger = badger2040.Badger2040()

# Connect to WiFi
badger.connect()

# Sync time
try:
    ntptime.settime()
    is_time_synced = True
    year, month, day, hour, minute, second, _, _ = time.localtime()
    print(
        "Time synced {}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(
            year, month, day, hour, minute, second
        )
    )
except:
    pass

PINS_BREAKOUT_GARDEN = {"sda": 4, "scl": 5}
i2c = PimoroniI2C(**PINS_BREAKOUT_GARDEN)
bme = BreakoutBME68X(i2c)

while True:
    # read sensor
    temperature, pressure, humidity, gas, status, _, _ = bme.read()
    year, month, day, hour, minute, second, _, _ = time.localtime()
    print(
        "{}/{:02d}/{:02d} {:02d}:{:02d}:{:02d} {:0.2f}°C, {:0.2f}%".format(
            year, month, day, hour, minute, second, temperature, humidity
        )
    )
    # set display
    badger.set_pen(15)
    badger.clear()
    badger.set_pen(0)
    badger.set_font('bitmap8')
    badger.text("{:0.2f}°C".format(temperature), 10, 10)
    badger.text("{:0.2f}%".format(humidity), 10, 30)
    badger.text("Updated: {}/{:02d}/{:02d} {:02d}:{:02d}:{:02d}".format(year, month, day, hour, minute, second), 10, 50)
    badger.text('Connected' if badger.isconnected() else 'Disconnected', 10, 70)
    badger.update()
    # upload data
    try:
        r = urequests.post(
            API,
            headers={
                "X-AIO-Key": API_KEY,
                "Content-Type": "application/json",
            },
            json={
                "feeds": [
                    {
                        "key": "temperature",
                        "value": temperature,
                    },
                    {
                        "key": "humidity",
                        "value": humidity,
                    },
                ]
            },
        )
        print(r.json())
        r.close()
    except:
        print("Failed to upload.", file=sys.stderr)
    # sleep
    time.sleep(60 * 5)
