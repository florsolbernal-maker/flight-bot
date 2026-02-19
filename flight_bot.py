import requests
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# =========================
# CONFIGURACIÓN
# =========================

API_KEY = "VM1HbkHRwIxwEiqZ7VzAW6VF4xEjpGt3"
API_SECRET = "yj0p0kRe2jGckX6P"

EMAIL = "flor.sol.bernal@gmail.com"
EMAIL_PASSWORD = "cdlefymxcqzaemeh"
EMAIL_DESTINO = "flor.sol.bernal@gmail.com"

ORIGINS = ["EZE", "AEP"]
DESTINATION = "PMI"

DATES = ["2026-03-23", "2026-03-24", "2026-03-25"]

MIN_PRICE = 550
MAX_PRICE = 750

# =========================
# TOKEN AMADEUS
# =========================

def get_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": API_SECRET
    }
    r = requests.post(url, data=data)
    return r.json()["access_token"]

# =========================
# BUSCAR VUELOS
# =========================

def search_flights(token, origin, date):
    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": DESTINATION,
        "departureDate": date,
        "adults": 1,
        "nonStop": "false",
        "max": 5,
        "currencyCode": "EUR"
    }

    r = requests.get(url, headers=headers, params=params)
    data = r.json()

    if "data" not in data:
        return None

    best = None

    for offer in data["data"]:
        price = float(offer["price"]["total"])
        airline = offer["validatingAirlineCodes"][0]
        segments = offer["itineraries"][0]["segments"]

        # Detectar si pasa por USA
        usa_airports = ["JFK", "MIA", "ATL", "ORD", "LAX", "DFW", "IAH"]
        stop_in_usa = any(seg["arrival"]["iataCode"] in usa_airports for seg in segments)

        if stop_in_usa:
            continue

        if MIN_PRICE <= price <= MAX_PRICE:
            best = {
                "price": price,
                "airline": airline,
                "date": date,
                "origin": origin
            }
            break

    return best

# =========================
# ENVIAR EMAIL
# =========================

def send_email(content):
    msg = MIMEText(content)
    msg["Subject"] = "🔥 Vuelo barato encontrado a Palma!"
    msg["From"] = EMAIL
    msg["To"] = EMAIL_DESTINO

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(EMAIL, EMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()

# =========================
# MAIN
# =========================

def main():
    token = get_token()

    for origin in ORIGINS:
        for date in DATES:
            result = search_flights(token, origin, date)

            if result:
                price = result["price"]
                airline = result["airline"]

                # Links útiles
                google_link = f"https://www.google.com/travel/flights?q={origin}%20to%20PMI%20{date}"
                skyscanner_link = f"https://www.skyscanner.com/transport/flights/{origin.lower()}/pmi/{date.replace('-','')}/"

                message = f"""
🔥 VUELO ENCONTRADO

Origen: {origin}
Destino: Palma de Mallorca (PMI)
Fecha: {date}
Aerolínea: {airline}
Precio: €{price}

🔎 Buscar en Google Flights:
{google_link}

✈ Buscar en Skyscanner:
{skyscanner_link}

Revisalo rápido porque estos precios duran poco.
"""

                send_email(message)
                print("Mail enviado con oferta")
                return

    print("No se encontraron ofertas en el rango.")

if __name__ == "__main__":
    main()
