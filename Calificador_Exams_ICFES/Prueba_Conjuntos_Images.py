import cv2
import os


imput_images_path = "C:/Users/NITRO 5/Desktop/Calificador_Exams_ICFES/Images_Exams"
file_names = os.listdir(imput_images_path)
# print(file_names)

output_images_path = "C:/Users/NITRO 5/Desktop/Calificador_Exams_ICFES/outpt_images"
if not os.path.exists(output_images_path):
    os.makedirs(output_images_path)
    

for file_names in file_names:
    images_path = imput_images_path + "/" + file_names
    image = cv2.imread(images_path)
    if image is None:
        continue
    cv2.imshow("image", image)
    cv2.waitKey(0)
cv2.destroyAllWindows()    

    