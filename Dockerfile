FROM python:3.14-slim

WORKDIR /app

# Instalacja zależności
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie kodu aplikacji
COPY . .

# Tworzenie folderów na bazę danych i obrazki (aby uniknąć problemów z uprawnieniami)
RUN mkdir -p instance/uploads instance/processed

# Domyślna komenda (zostanie nadpisana w docker-compose dla workera)
CMD ["flask", "run", "--host=0.0.0.0"]
