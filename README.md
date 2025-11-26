# Flask + Celery + RabbitMQ: Priority Image Processing POC

Aplikacja Proof of Concept (POC). Demonstruje wykorzystanie asynchronicznego przetwarzania zadań z użyciem **kolejek priorytetowych**.

System pozwala użytkownikom przesyłać zdjęcia do rozmycia (Blur). Zalogowani użytkownicy (VIP) są obsługiwani przez kolejkę priorytetową (`high_priority`), podczas gdy goście trafiają do kolejki zwykłej (`low_priority`).

## 🚀 Główne Funkcjonalności

* **Asynchroniczność:** Przetwarzanie obrazów odbywa się w tle dzięki **Celery** i **RabbitMQ**, nie blokując interfejsu użytkownika.
* **Kolejki Priorytetowe:**
    * 🛑 **Anonim:** Zadania trafiają do kolejki `low_priority`.
    * 👑 **Zalogowany:** Zadania trafiają do kolejki `high_priority` i są pobierane przez workera w pierwszej kolejności.
* **Symulacja Obciążenia:** Worker posiada sztuczne opóźnienie (`time.sleep`) oraz przetwarza zadania sekwencyjnie (`concurrency=1`), aby uwydatnić działanie kolejki.
* **Nowoczesny UI:** Interfejs oparty na **Bootstrap 5** w trybie Dark Mode, w pełni responsywny.
* **Architektura Docker:** Całość (Web, Worker, Broker) uruchamiana jednym poleceniem dzięki Docker Compose.
* **Współdzielony Wolumen:** Bezpieczna wymiana plików wyników między kontenerami poprzez dedykowany wolumen Dockera.

## 🛠️ Stack Technologiczny

* **Backend:** Python 3.14, Flask
* **Task Queue:** Celery 5.x
* **Message Broker:** RabbitMQ 3 Management
* **Image Processing:** Pillow (PIL)
* **Containerization:** Docker & Docker Compose
* **Frontend:** HTML5, CSS3, Bootstrap 5.3

## 📂 Struktura Projektu

```text
├── flaskr/                 # Kod źródłowy aplikacji
│   ├── templates/          # Szablony HTML (Bootstrap)
│   ├── static/             # CSS
│   ├── __init__.py         # Fabryka aplikacji i konfiguracja Celery
│   ├── image.py            # Endpointy uploadu i sprawdzania statusu
│   ├── tasks.py            # Logika workera (blur + sleep)
│   └── ...
├── docker-compose.yaml     # Orkiestracja kontenerów
├── Dockerfile              # Obraz dla Web i Workera
├── requirements.txt        # Zależności Python
├── benchmark.py            # Skrypt testujący priorytetyzację
└── README.md
````

## ⚙️ Instalacja i Uruchomienie

Wymagany jest zainstalowany **Docker** oraz **Docker Compose**.

1.  **Sklonuj repozytorium (lub wejdź do folderu projektu):**

    ```bash
    cd image-blur-queues
    ```

2.  **Uruchom środowisko:**
    Użyj flagi `--build` przy pierwszym uruchomieniu, aby zbudować obrazy.

    ```bash
    docker-compose up --build
    ```

3.  **Dostęp do aplikacji:**

      * Aplikacja Webowa: [http://localhost:5000](http://localhost:5000)
      * Panel RabbitMQ: [http://localhost:15672](http://localhost:15672) (Login: `guest`, Hasło: `guest`)

---
