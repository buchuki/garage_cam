import datetime
import time
import traceback

import requests
from twilio.rest import Client as TwilioClient

from learning import predict
from util import latest_image, image_date, get_ftp_files

import config


def send_message(status):
    if status == "OPEN":
        event_name = "garage_door_opened"
    else:
        event_name = "garage_door_closed"
    url = f"https://maker.ifttt.com/trigger/{event_name}/with/key/{config.ifttt_key}"
    requests.post(url)


def send_warning_message(last_change):
    event_name = "garage_door_warning"
    url = f"https://maker.ifttt.com/trigger/{event_name}/with/key/{config.ifttt_key}?value1={last_change.strftime('%H:%M')}"

    requests.post(url)

    twilio = TwilioClient(config.twilio["account"], config.twilio["token"])
    twilio.messages.create(
        to=config.twilio["to"],
        from_=config.twilio["from"],
        body=f"Garage door has been open since {last_change:%H:%M}",
    )


def message_loop():
    source_dir = config.options.data_dir / "source"
    last_image = latest_image()
    last_status = predict(last_image)
    last_change = image_date(last_image)
    print(f"Current status: {last_status} at {last_change:%Y-%m-%d %H:%M}")

    while True:
        try:
            get_ftp_files(**config.ftp, source_dir=source_dir)
            last_image = latest_image()
            current_status = predict(latest_image())
            if (
                last_status == "OPEN"
                and (datetime.datetime.now() - last_change).seconds
                > config.open_warning_seconds
            ):
                print(f"Warning: Door has been open since {last_change:%Y-%m-%d %H:%M}")
                send_warning_message(last_change)
                last_change = datetime.datetime.now()

            if current_status != last_status:
                last_change = image_date(last_image)
                print(f"Status changed to {current_status}")
                send_message(current_status)
            last_status = current_status

            time.sleep(293)
        except Exception as ex:
            traceback.print_exc()
