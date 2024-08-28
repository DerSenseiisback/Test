import os
import requests
import zipfile
import logging
from pdf2image import convert_from_path
import pytesseract

# Logger initialisieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# GitHub-Zugangsdaten
GITHUB_TOKEN = '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'
GITHUB_REPO = 'DerSenseiisback/Vertrag'
GITHUB_FILE_TESSERACT = 'Source%20Files/Tesseract/tesseract.exe'
GITHUB_FILE_POPPLER_ZIP = 'Source%20Files/Poppler/Library/bin'

# Pfade setzen
TESSERACT_PATH = os.path.join(os.getcwd(), 'Tesseract/tesseract.exe')
POPPLER_PATH = os.path.join(os.getcwd(), 'Poppler/bin')

# Verzeichnisse erstellen, falls sie nicht existieren
os.makedirs(os.path.join(os.getcwd(), 'Tesseract'), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), 'Poppler/bin'), exist_ok=True)

# Tesseract herunterladen
if not os.path.isfile(TESSERACT_PATH):
    logger.info("Tesseract wird heruntergeladen...")
    url = f"https://{GITHUB_TOKEN}@raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_FILE_TESSERACT}"
    response = requests.get(url)
    if response.status_code == 200:
        with open(TESSERACT_PATH, 'wb') as f:
            f.write(response.content)
        logger.info("Tesseract erfolgreich heruntergeladen.")
    else:
        logger.error(f"Tesseract konnte nicht heruntergeladen werden. Status Code: {response.status_code}")
else:
    logger.info("Tesseract ist bereits vorhanden.")

# Überprüfen, ob Tesseract existiert
if os.path.isfile(TESSERACT_PATH):
    logger.info(f"Tesseract erfolgreich installiert unter {TESSERACT_PATH}")
else:
    logger.error(f"Tesseract konnte nicht gefunden werden unter {TESSERACT_PATH}")

# Poppler herunterladen und entpacken
if not os.path.exists(POPPLER_PATH):
    logger.info("Poppler wird heruntergeladen...")
    url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}/archive/refs/heads/main.zip"
    response = requests.get(url)
    
    if response.status_code == 200:
        zip_path = os.path.join(os.getcwd(), 'poppler.zip')
        with open(zip_path, 'wb') as f:
            f.write(response.content)

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(os.getcwd())

            poppler_bin_src = os.path.join(os.getcwd(), 'Vertrag-main/Source Files/Poppler/Library/bin')
            for root, dirs, files in os.walk(poppler_bin_src):
                for file in files:
                    os.rename(os.path.join(root, file), os.path.join(POPPLER_PATH, file))
            logger.info("Poppler erfolgreich heruntergeladen und entpackt.")
        except zipfile.BadZipFile:
            logger.error("Das heruntergeladene Poppler-Archiv ist beschädigt.")
    else:
        logger.error(f"Poppler konnte nicht heruntergeladen werden. Status Code: {response.status_code}")
else:
    logger.info("Poppler ist bereits vorhanden.")

# Überprüfen, ob Poppler existiert
if os.path.exists(POPPLER_PATH) and len(os.listdir(POPPLER_PATH)) > 0:
    logger.info(f"Poppler erfolgreich installiert unter {POPPLER_PATH}")
else:
    logger.error(f"Poppler konnte nicht gefunden werden unter {POPPLER_PATH}")

# Sicherstellen, dass die Umgebungsvariablen gesetzt sind
os.environ['TESSERACT_PATH'] = TESSERACT_PATH
os.environ['POPPLER_PATH'] = POPPLER_PATH

# Setze den Tesseract-Pfad in pytesseract
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

def check_poppler_tesseract(pdf_path):
    try:
        logger.info("Beginne mit der Verarbeitung des PDFs...")
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        for i, image in enumerate(images):
            text = pytesseract.image_to_string(image, lang='deu')
            logger.info(f"Text auf Seite {i + 1}:\n{text}")
    except Exception as e:
        logger.error(f"Ein Fehler ist aufgetreten: {e}", exc_info=True)

# Teste die Installation mit einem Beispiel-PDF
pdf_path = r"C:\Users\logiermann\OneDrive - Bachert Unternehmensberatung GmbH & Co. KG\Documents\Python\Py Kredit\KI Verträge\A.9.i. Commerzbank.pdf"
check_poppler_tesseract(pdf_path)
