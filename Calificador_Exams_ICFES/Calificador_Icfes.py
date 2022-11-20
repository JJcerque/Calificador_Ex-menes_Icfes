import cv2
import utlis
import numpy as np
import pandas as pd
from pandas import ExcelWriter
import os
from pytesseract import *
import openpyxl
pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'   #Ubicación del tesseract


# Autores: Juan José Cerquera G. & Juan Ruiz

consultar = ""
nota = []
nombre = []

while consultar != "N": 
    
    # Leer carpeta con imágines
    imput_images_path = "C:/Users/NITRO 5/Desktop/Calificador_Exams_ICFES/Images_Exams"
    file_names = os.listdir(imput_images_path)
    
    output_images_path = "C:/Users/NITRO 5/Desktop/Calificador_Exams_ICFES/outpt_images"
    if not os.path.exists(output_images_path):
        os.makedirs(output_images_path)
    
    count = 0
    
    for file_names in file_names:
        images_path = imput_images_path + "/" + file_names
        img = cv2.imread(images_path)
        if img is None:
            continue
        name = input("Ingrese nombre del estudiante: ")
        nombre.append(name)
        scale_percent = 39
        width = int(img.shape[1] * scale_percent/100)
        height = int(img.shape[0] * scale_percent/100)
        dim = (width, height)

        questions = 5
        choices = 5
        ans = [0,3,1,4,2]

        #PROCESAMIENTO
        resized = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
        imgCountours = resized.copy()
        imgFinal = resized.copy()
        imgBiggestCountours = resized.copy()
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(gray,(5,5),1)
        canny = cv2.Canny(gray, 10, 50)

        #ENCONTRAR CONTORNOS
        countours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cv2.drawContours(resized, countours, -1, (0, 255, 0), 10)

        #ENCONTRAR RECTANGULOS
        rectCon = utlis.rectCountour(countours)
        biggestCountour = utlis.getCornerPoints(rectCon[0])
        gradePoints = utlis.getCornerPoints(rectCon[1])
        # print(rectCon)

        if biggestCountour.size != 0 and gradePoints.size != 0:
            cv2.drawContours(imgBiggestCountours, biggestCountour, -1, (0,255,0),20)
            cv2.drawContours(imgBiggestCountours, gradePoints, -1, (255,0,0),20)

            biggestCountour = utlis.reorder(biggestCountour)
            gradePoints = utlis.reorder(gradePoints)
            
            # Ajuste de la imágen para análisis de cada una de las partes de la hoja de respuestas
            pt1 = np.float32(biggestCountour)
            pt2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
            matrix = cv2.getPerspectiveTransform(pt1,pt2)
            imgWarpColored = cv2.warpPerspective(resized, matrix, (width, height))

            ptG1 = np.float32(gradePoints)
            ptG2 = np.float32([[0, 0], [325, 0], [0, 150], [325, 150]])
            matrixG = cv2.getPerspectiveTransform(ptG1,ptG2)
            imgGradeDisplay = cv2.warpPerspective(resized, matrixG, (width, height))
            # cv2.imshow("Grade", imgWarpColored)
            
            # Aplicar Filtros para el reconocimiento de las respuestas
            imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
            imgThresh = cv2.threshold(imgWarpGray, 135, 255, cv2.THRESH_BINARY_INV)[1]
            boxes = utlis.splitBoxes(imgThresh)
        
        # Obtener NO ZERO PIXEL VALUES
            myPixelVal = np.zeros((questions, choices))
            countC = 0
            countR = 0
        
            # print(cv2.countNonZero(boxes[1]), cv2.countNonZero(boxes[2]))
            # cv2.imshow("Test", boxes[1])
            # cv2.imshow("Test", boxes[2])
            
        # Reconocedor de respuestas
            for image in boxes:
                totalPixels = cv2.countNonZero(image)   
                myPixelVal[countR][countC] = totalPixels
                countC += 1
                if (countC == choices): countR += 1; countC = 0
            print(myPixelVal)     
            
            # Encontrar las marcas hechas en la hoja de respeustas
            myIndex = []       
            for x in range (0, questions):
                arr = myPixelVal[x]
                myIndexlVal = np.where(arr == np.amax(arr)) 
                # print(myIndexlVal[0])
                myIndex.append(myIndexlVal[0][0])
            # print(myIndex)
            
            
            # Calificar
            grading = []
            for x in range (0, questions):
                if ans[x] == myIndex[x]:
                    grading.append(1)
                else:
                    grading.append(0)
            # print(grading)
            
            score = (sum(grading)/questions) * 100
            print("Su nota es", score)
            nota.append(score)

            # Muestra de resultados
            imgResult = imgWarpColored.copy()
            imgResult = utlis.showAnswers(imgResult, myIndex, grading, ans, questions, choices)
            imgRawDrawing = np.zeros_like(imgWarpColored)
            imgRawDrawing = utlis.showAnswers(imgRawDrawing, myIndex, grading, ans, questions, choices)
            invMatrix = cv2.getPerspectiveTransform(pt2,pt1)
            imgInvWarp = cv2.warpPerspective(imgRawDrawing, invMatrix, (width, height))
            imgRawGrade = np.zeros_like(imgGradeDisplay)
            cv2.putText(imgRawGrade, str(int(score)) + "%", (50, 100), cv2.FONT_HERSHEY_COMPLEX, 3, (0, 255, 255), 3)
            invMatrixG = cv2.getPerspectiveTransform(ptG2,ptG1)
            imgInvGradeDisplay = cv2.warpPerspective(imgRawGrade, invMatrixG, (width, height))
        
            # Se superpone las imágenes analisadas para brindar una imágen final con los resultados
            imgF = cv2.addWeighted(resized, 1, imgInvWarp, 1, 0)
            imgF1 = cv2.addWeighted(imgF, 1, imgInvGradeDisplay, 1, 0)
            
            # Crea carpeta con las imágenes resultantes de los exámenes
            cv2.imwrite(output_images_path + "/imgF1" + str(count) + ".jpg", imgF1)
            count += 1

            cv2.imshow('Exam', imgF1)
            cv2.waitKey(0)
    
    consultar = input("Desea seguir? Y/N")
  

    data = {'Nombre' : nombre, 'NOTA': nota}

df = pd.DataFrame(data)

# Crea y llena excel con los resultados de los exámenes
escritor = pd.ExcelWriter('C:/Users/NITRO 5/Desktop/Calificador_Exams_ICFES/Calificaciones.xlsx', engine ='xlsxwriter')
df.to_excel(escritor, sheet_name="hoja1", index=False)
escritor.save()

print("Se han subido los datos con exito")
