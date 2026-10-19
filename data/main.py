import datetime
import json
import logging

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

what_time = datetime.datetime.now()

url = [
    "https://bimasislam.kemenag.go.id/jadwalshalat",
    "https://bimasislam.kemenag.go.id/ajax/getKabkoshalat",
    "https://bimasislam.kemenag.go.id/ajax/getShalatbln",
]

provinsi = []
kabkot = []


def build_session():
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "POST"}),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    scraper_session = requests.Session()
    scraper_session.mount("https://", adapter)
    scraper_session.mount("http://", adapter)
    scraper_session.headers.update(
        {
            "User-Agent": "jadwal-salat-indonesia-scraper/1.0",
            "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
        }
    )
    return scraper_session


session = build_session()


def get_provinces():
    response = session.get(url[0], timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    select = soup.find("select", {"id": "search_prov"})

    if select is None:
        raise RuntimeError("Elemen select provinsi tidak ditemukan pada halaman Kemenag")

    for option in select.find_all("option")[1:]:
        value = option.get("value")
        nama = option.get_text(strip=True)
        if value and nama:
            provinsi.append({nama: value})


def get_regencies():
    for tiap_provinsi in provinsi:
        prov_name, prov_value = next(iter(tiap_provinsi.items()))
        payload = {"x": prov_value}

        try:
            response = session.post(url[1], data=payload, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as error:
            logging.warning("Gagal mengambil kabupaten untuk %s: %s", prov_name, error)
            continue

        options = soup.find_all("option")
        if not options:
            logging.warning("Tidak ada kabupaten ditemukan untuk %s", prov_name)

        for option in options:
            value = option.get("value")
            nama = option.get_text(strip=True)
            if value and nama:
                kabkot.append({nama: value})


def get_jadwal():
    for provinsi_item in provinsi:
        prov_name, prov_value = next(iter(provinsi_item.items()))

        for kabupaten_item in kabkot:
            kabupaten_name, kabupaten_value = next(iter(kabupaten_item.items()))
            payload = {
                "x": prov_value,
                "y": kabupaten_value,
                "bln": what_time.month,
                "thn": what_time.year,
            }

            try:
                response = session.post(url[2], data=payload, timeout=30)
                response.raise_for_status()

                # Endpoint kadang mengembalikan body kosong/HTML, bukan JSON.
                if not response.content.strip():
                    raise ValueError("respons kosong")

                soup_dict = response.json()
                if not isinstance(soup_dict, dict):
                    raise ValueError("format JSON bukan object")
            except (requests.RequestException, ValueError, json.JSONDecodeError) as error:
                logging.warning(
                    "Melewati %s / %s karena respons jadwal tidak valid: %s",
                    prov_name,
                    kabupaten_name,
                    error,
                )
                continue

            if soup_dict.get("status") != 1:
                continue

            soup_json = json.dumps(
                soup_dict, sort_keys=True, indent=4, ensure_ascii=False
            )
            filename = (
                f"{prov_name} {kabupaten_name} "
                f"{what_time.month} {what_time.year}.json"
            )
            with open(filename, "w", encoding="utf-8") as json_file:
                json_file.write(soup_json)


get_provinces()
get_regencies()
get_jadwal()
