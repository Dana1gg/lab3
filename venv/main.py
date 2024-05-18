import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import requests
from flask import Flask, request, render_template


app = Flask(__name__,static_folder='C:/uploads')


UPLOAD_FOLDER = 'C:/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

SECRET_KEY = "6LeJFtApAAAAAA9e7wBn0hC2mJo2NIOM5kDZ8MBN"
SITE_KEY = "6LeJFtApAAAAACGMGgam1GpQGBrEoowXhGEOaJIK"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Проверка Google reCAPTCHA
        recaptcha_response = request.form.get('g-recaptcha-response')
        if not verify_recaptcha(recaptcha_response):
            return "Ошибка проверки капчи"

        file = request.files['image']
        #Создание пути к файлу изображения, используя конфигурацию папки загрузки и имя файла.
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        #Сохранение файла изображения по указанному пути на сервере.
        file.save(file_path)
        #Открытие изображения с помощью библиотеки PIL (Pillow) по указанному пути.
        image = Image.open(file_path)

        scale = float(request.form['scale'])
        new_width = int(image.width * scale)
        new_height = int(image.height * scale)
        rotated_image = image.resize((new_width, new_height))
        rotated_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'rotated_image.png')
        rotated_image.save(rotated_image_path)


        # Создание гистограмм для изображений
        bins = int(request.form['bins'])
        original_hist = np.histogram(image.getdata(), bins=bins)[0]
        rotated_image = image.rotate(90)
        rotated_hist = np.histogram(rotated_image.getdata(), bins=bins)[0]
        # Создаем и сохраняем гистограммы
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.plot(original_hist, color='b')
        plt.title('Original Image Histogram')
        plt.xlabel('Интенсивность пикселей')
        plt.ylabel('Частота')
        plt.subplot(1, 2, 2)
        plt.plot(rotated_hist, color='r')
        plt.title('Rotated Image Histogram')
        plt.xlabel('Интенсивность пикселей')
        plt.ylabel('Частота')

        histograms_path = os.path.join(app.config['UPLOAD_FOLDER'], 'histograms.png')
        plt.savefig(histograms_path)git init

        return render_template('index.html',original_image=file.filename,rotated_image='rotated_image.png',histograms='histograms.png')

    return render_template('index.html', site_key=SITE_KEY)

def verify_recaptcha(recaptcha_response):
    payload = {
        'secret': SECRET_KEY,
        'response': recaptcha_response
    }
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
    result = response.json()
    return result['success']

if __name__ == '__main__':
    app.run(debug=True)