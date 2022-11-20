import cv2
from pytesseract import *
pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
img = cv2.imread("Ex2.2.jpg")
Img2 = img.copy()
#NAME
scale_percent2 = 260
width2 = int(Img2.shape[1] * scale_percent2/290)
height2 = int(Img2.shape[0] * scale_percent2/100)
dim2 = (width2, height2)
resized2 = cv2.resize(Img2, dim2, interpolation=cv2.INTER_AREA)

resultado = pytesseract.image_to_string(resized2)
cv2.imshow("P1", resized2)
print(resultado)