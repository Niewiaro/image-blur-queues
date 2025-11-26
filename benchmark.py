import requests
import time
import threading
import io
import random
from PIL import Image, ImageDraw

# --- KONFIGURACJA ---
BASE_URL = "http://localhost:5000"
VIP_USERNAME = "user"
VIP_PASSWORD = "user"
ANONIM_TASKS_COUNT = 5
VIP_DELAY = 2.0


def generate_random_image():
    """
    Tworzy obrazek z losowymi, kontrastowymi liniami w pamięci.
    Idealny do testowania efektu blur.
    """
    width, height = 200, 200

    # 1. Ciemne tło (żeby jasne linie były widoczne)
    bg_color = (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50))
    img = Image.new("RGB", (width, height), color=bg_color)

    # Tworzymy obiekt do rysowania
    draw = ImageDraw.Draw(img)

    # 2. Rysujemy 20 losowych linii
    for _ in range(20):
        # Losowe współrzędne początku i końca linii
        x1 = random.randint(0, width)
        y1 = random.randint(0, height)
        x2 = random.randint(0, width)
        y2 = random.randint(0, height)

        # Jasny, losowy kolor linii dla kontrastu
        line_color = (
            random.randint(150, 255),
            random.randint(150, 255),
            random.randint(150, 255),
        )

        # Losowa grubość linii
        thickness = random.randint(1, 5)

        draw.line([(x1, y1), (x2, y2)], fill=line_color, width=thickness)

    # 3. Zapisujemy do bufora w pamięci
    img_byte_arr = io.BytesIO()
    # Używamy PNG, bo jest bezstratny i lepiej zachowuje ostre krawędzie przed blurem
    # (JPEG mógłby sam z siebie dodać "szum" na krawędziach)
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)  # Przewijamy "taśmę" na początek pliku
    return img_byte_arr


def login():
    """Loguje użytkownika i zwraca sesję (ciasteczka)."""
    session = requests.Session()
    try:
        # 1. GET logowania (dla CSRF/ciastek inicjalnych)
        session.get(f"{BASE_URL}/auth/login")
        # 2. POST logowania
        res = session.post(
            f"{BASE_URL}/auth/login",
            data={"username": VIP_USERNAME, "password": VIP_PASSWORD},
        )
        # Sprawdzamy czy przekierowało na stronę główną (sukces)
        if res.url.strip("/") == BASE_URL.strip("/"):
            print(f"🔑 Zalogowano pomyślnie jako: {VIP_USERNAME}")
            return session
        else:
            print(f"❌ Błąd logowania! Sprawdź login/hasło. (Aktualny URL: {res.url})")
            exit(1)
    except Exception as e:
        print(f"❌ Nie można połączyć się z serwerem: {e}")
        exit(1)


def send_request_and_wait(session, name):
    """Wysyła zdjęcie i czeka na zakończenie przetwarzania."""

    # Generujemy świeży obrazek dla każdego requestu
    img_data = generate_random_image()
    files = {"file": (f"{name}.jpg", img_data, "image/jpeg")}

    print(f"📤 [{name}] Wysyłanie...")
    start_time = time.time()

    try:
        # Wysyłka (z sesją lub bez)
        if session:
            res = session.post(f"{BASE_URL}/image/upload", files=files)
        else:
            res = requests.post(f"{BASE_URL}/image/upload", files=files)

        if res.status_code != 202:
            print(f"❌ [{name}] Błąd uploadu: {res.text}")
            return

        data = res.json()
        task_id = data["task_id"]
        queue = data["queue"]
        print(f"📥 [{name}] Przyjęto (Kolejka: {queue})")

        # Pętla sprawdzająca status (Polling)
        while True:
            status_res = requests.get(f"{BASE_URL}/image/status/{task_id}")
            status_data = status_res.json()

            if status_data["status"] == "SUCCESS":
                duration = time.time() - start_time
                print(f"🏁 [{name}] UKOŃCZONO w {duration:.2f}s!")
                break
            elif status_data["status"] == "FAILURE":
                print(f"💀 [{name}] AWARIA ZADANIA!")
                break

            # Czekamy 1s przed kolejnym sprawdzeniem
            time.sleep(1)

    except Exception as e:
        print(f"❌ [{name}] Wyjątek: {e}")


# --- START PROGRAMU ---


def main():
    print("--- START BENCHMARKU ---")

    # 1. Przygotowanie sesji VIP
    vip_session = login()

    threads = []

    # 2. Wysyłamy armię anonimów
    print(f"\n🌊 Wypuszczam {ANONIM_TASKS_COUNT} anonimowych zapytań...")
    for i in range(1, ANONIM_TASKS_COUNT + 1):
        t = threading.Thread(target=send_request_and_wait, args=(None, f"Anonim-{i}"))
        threads.append(t)
        t.start()
        time.sleep(0.2)  # Mały odstęp żeby requesty weszły w naturalnej kolejności

    # 3. Czekamy chwilę, żeby anonimy na pewno zapchały kolejkę
    print(f"\n⏳ Czekam {VIP_DELAY}s zanim wpuszczę VIP-a...")
    time.sleep(VIP_DELAY)

    # 4. Wchodzi VIP
    print("\n🚀 Wchodzi VIP (powinien przeskoczyć oczekujących anonimów)!")
    vip_thread = threading.Thread(
        target=send_request_and_wait, args=(vip_session, "VIP-USER")
    )
    threads.append(vip_thread)
    vip_thread.start()

    # 5. Czekamy na wszystkich
    for t in threads:
        t.join()

    print("\n--- KONIEC TESTU ---")


if __name__ == "__main__":
    main()
