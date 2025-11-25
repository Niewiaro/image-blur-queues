import time
import os
from celery import shared_task
from PIL import Image, ImageFilter


@shared_task(ignore_result=False)
def process_image(filename, destination_folder):
    """
    To zadanie wykonuje się w tle.
    """
    input_path = os.path.join(destination_folder, "uploads", filename)
    output_dir = os.path.join(destination_folder, "processed")
    output_path = os.path.join(output_dir, filename)

    print(f"--> [START] Przetwarzanie obrazu: {filename}")

    os.makedirs(output_dir, exist_ok=True)

    # 1. Otwarcie obrazu
    with Image.open(input_path) as img:
        # 2. Nakładanie filtra (Blur)
        blurred_img = img.filter(ImageFilter.GaussianBlur(radius=10))

        # 3. SZTUCZNE OPÓŹNIENIE (aby wykazać działanie kolejki)
        print(f"--> [WAIT] Czekam 10 sekund dla: {filename}")
        time.sleep(10)

        # 4. Zapis wyniku
        blurred_img.save(output_path)

    print(f"--> [KONIEC] Obraz gotowy: {output_path}")

    # Zwracamy tylko dane sukcesu. W przypadku błędu, funkcja rzuci wyjątek
    # i ten return nigdy się nie wykona (co jest poprawne).
    return {"filename": filename}
