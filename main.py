import uvicorn
from fastapi import FastAPI, HTTPException
from requests import get
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()

app = FastAPI()


@app.get("/print/{cable_id}")
async def print_cable(cable_id: int):
    data = filter_netbox_data(get_nextbox_data(cable_id))
    print_label(data)
    return {"Success"}


def get_nextbox_data(cable_id: int) -> dict:
    url = f"https://{os.getenv('NETBOX_HOST')}/api/dcim/cables/?id={cable_id}"
    response = get(url, headers={'Authorization': f'token {os.getenv("NETBOX_APITOKEN")}'})
    device = response.json()
    if device['count'] == 1:
        return device['results'][0]
    else:
        raise HTTPException(status_code=404, detail="Cable was not found in Netbox")


def filter_netbox_data(cable_data: dict) -> list[dict]:
    return [
        dict(
            device_name=cable_data['a_terminations'][0]['object']['device']['name'],
            device_interface=cable_data['a_terminations'][0]['object']['name'],
        ),
        dict(
            device_name=cable_data['b_terminations'][0]['object']['device']['name'],
            device_interface=cable_data['b_terminations'][0]['object']['name'],
        )
    ]


def print_label(labels: list) -> None:
    build_str = "/home/laph/bin/ptouch-print"
    for label in labels:
        build_str += (f' --cutmark --pad 5 --text "{label["device_name"]}" "{label["device_interface"]}" --pad 5 '*2)
    subprocess.run([build_str], shell=True)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
