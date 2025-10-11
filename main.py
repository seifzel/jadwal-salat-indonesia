import requests
import datetime
import hashlib
import json
from bs4 import BeautifulSoup

what_time = datetime.datetime.now()
session = requests.Session()
url = [
    "https://bimasislam.kemenag.go.id/jadwalshalat",
    "https://bimasislam.kemenag.go.id/ajax/getKabkoshalat",
    "https://bimasislam.kemenag.go.id/ajax/getShalatbln"]
provinsi = []
kabkot = []


def get_key_by_value(dictionary, value):
    return next((k for k, v in dictionary.items() if v == value), None)

def get_provinces():
    response = session.get(url[0])
    response = session.get(url[0])
    soup = BeautifulSoup(response.content, 'html.parser')
    select = soup.find('select', {'id': 'search_prov'})

    for option in select.find_all('option')[1:]:
        value = option.get('value')
        nama = option.get_text(strip=True)
        provinsi.append({nama : value})

def get_regencies():
    for tiap_provinsi in provinsi:
        for key, value in tiap_provinsi.items():
            payload = {"x": value}
            response = session.post(url[1], data=payload, cookies=session.cookies.get_dict())
            soup = BeautifulSoup(response.content, 'html.parser')
            for option in soup.find_all('option'):
                value = option.get('value')
                nama = option.get_text(strip=True)
                kabkot.append({nama : value})

def get_jadwal():
    for x in provinsi:
        prov = next(iter(x))
        res_x = x[prov]
        for y in kabkot:
            kk = next(iter(y))
            res_y = y[kk]
            payload = {
                "x": res_x,
                "y": res_y,
                "bln": what_time.month,
                "thn": what_time.year}

            response = session.post(url[2], data=payload, cookies=session.cookies.get_dict())

            soup = BeautifulSoup(response.content, 'html.parser')
            soup_dict = json.loads(str(soup))

            if soup_dict["status"] == 1:
                soup_json = json.dumps(soup_dict, sort_keys=True, indent=4, ensure_ascii=False)
                with open(get_key_by_value(x, res_x)+' '+get_key_by_value(y, res_y)+' '+str(what_time.month)+' '+str(what_time.year)+'.json', 'w') as json_file:
                    json_file.write(soup_json)
            else:
                continue

get_provinces()
get_regencies()
get_jadwal()