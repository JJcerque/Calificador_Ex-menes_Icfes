import cv2
from pytesseract import *
pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
img = cv2.imread('Captura de pantalla 2022-11-15 092021.png')
resultado = pytesseract.image_to_string(img)
print(resultado)