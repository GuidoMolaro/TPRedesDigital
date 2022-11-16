import math
from datetime import datetime

import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler
import pandas as pd
import os


def post(fileName):
    files = {'file': open(fileName, 'rb')}
    r = requests.post("http://localhost:8080/upload", files=files)
    print(r.text)


def delete():
    r = requests.delete("http://localhost:8080/")
    print(r.text)


def saveData(data):
    arraySize = len(data) / 128
    tempData = [0 for i in range(math.ceil(arraySize))]
    j = 0
    for i in range(len(data)):
        if i % 128 == 0:
            tempData[j] = data._get_value(i, 'BPM')
            j = j + 1
    return tempData


class MyEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        print(event.src_path, "created.")
        if os.path.exists(event.src_path):
            if event.src_path.lower().endswith('.csv'):
                data = pd.read_csv(event.src_path, header=2)
                data = data.drop(columns=["Unnamed: 2"])  # elimina la columna de Nans
                temp = saveData(data)
                pd.DataFrame(temp).to_csv("./heartRate/hr.csv")
                os.remove(event.src_path)
                post("./heartRate/hr.csv")


observer = Observer()
observer.schedule(MyEventHandler(), ".", recursive=False)
observer.start()

try:
    while observer.is_alive():
        observer.join(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
