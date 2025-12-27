import requests
import datetime
import os
from twilio.rest import Client

LAT = 44.0805
LON = -103.2310

OW_KEY = os.environ["OW_KEY"]
TW_SID = os.environ["TW_SID"]
TW_TOKEN = os.environ["TW_TOKEN"]
FROM = os.environ["TW_FROM"]
TO = os.environ["TW_TO"]

now = datetime.datetime.now(datetime.timezone.utc)
local = now - datetime.timedelta(hours=7)

r = requests.get(
    "https://api.openweathermap.org/data/3.0/onecall",
    params={
        "lat": LAT,
        "lon": LON,
        "exclude": "current,minutely,daily",
        "units": "imperial",
        "appid": OW_KEY
    }
)

hours = r.json()["hourly"][:12]
snow_time = None

for h in hours:
    if "snow" in h["weather"][0]["main"].lower() or h.get("pop", 0) >= 0.4:
        snow_time = datetime.datetime.fromtimestamp(h["dt"], tz=datetime.timezone.utc) - datetime.timedelta(hours=7)
        break

sent_today = os.path.exists("sent.txt")
send = False

if snow_time and not sent_today:
    if local.hour < 22 and 0 < (snow_time - local).total_seconds() <= 7200:
        send = True
    if local.hour == 21:
        send = True

if send:
    Client(TW_SID, TW_TOKEN).messages.create(
        body="Snow expected overnight in Rapid City. Put the snow visor on.",
        from_=FROM,
        to=TO
    )
    open("sent.txt", "w").write("sent")
