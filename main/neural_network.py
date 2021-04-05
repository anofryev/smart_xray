from .models import Instance
import tensorflow
from tensorflow import keras
import os
import matplotlib.pyplot as plt
import cv2
import numpy as np
from pathlib import Path

def nn_predict():

    BASE_DIR = Path(__file__).resolve().parent.parent

    # Инициализируем нейросеть
    try:
        print(tensorflow.version)
        model = keras.models.load_model('D:/xray_model_tuned.h5')
    except Exception as e:
        print('Ошибка при инициализации нейросети: {0}'.format(e))
        return

    # Загружаем инстансы без предсказаний из БД
    try:
        instances = Instance.objects.filter(is_analized=False)
    except Exception as e:
        print('Ошибка при загрузке инстансов из БД: {0}'.format(e))
        return
    try:
        for instace in instances: # Для каждого загруженного инстанса:
            image_url = instace.image.url # Получаем ссылку на хранящуюся фото, относящуюся к инстансу
            absolute_url = str(BASE_DIR) + image_url
            print('BASE DIR: {0}'.format(BASE_DIR))
            print('image_url: {0}'.format(image_url))
            print('absolute : {0}'.format(str(BASE_DIR) + image_url))
            image = cv2.imread(absolute_url, cv2.IMREAD_GRAYSCALE)
            print('image загружен, type: {0}, shape: {1}'.format(type(image), np.shape(image)))
            IMG_SIZE = 180
            image_resized = cv2.resize(image, (IMG_SIZE, IMG_SIZE))
            image_resized = image_resized / 255
            image_resized = np.expand_dims(image_resized, axis=0)
            image_resized = np.expand_dims(image_resized, axis=0)
            image_resized = image_resized.reshape(-1, IMG_SIZE, IMG_SIZE, 1)
            result = model.predict_proba(image_resized) # Результат предсказания
            instace.probability = float(result[0][0]) #Вероятность наличия аномалии присваиваем свойству probability модели
            instace.is_analized = True # Выставляем флаг "Проанализирован"
            instace.save()  # Сохраняем изменения в инстансе
    except Exception as e:
        print('Ошибка при предсказании: {0}'.format(e))
        return
