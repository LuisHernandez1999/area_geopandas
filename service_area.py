import os
import cv2
import numpy as np
import folium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from shapely.geometry import Polygon
from shapely.ops import transform
import pyproj
import tkinter as tk
from tkinter import messagebox
import time
import platform

class DesmatamentoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Detector de Desmatamento")

        self.coords = []
        tk.Label(root, text="Longitude:").grid(row=0, column=0)
        self.lon_entry = tk.Entry(root)
        self.lon_entry.grid(row=0, column=1)

        tk.Label(root, text="Latitude:").grid(row=1, column=0)
        self.lat_entry = tk.Entry(root)
        self.lat_entry.grid(row=1, column=1)

        tk.Button(root, text="Adicionar Coordenada", command=self.add_coord).grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(root, text="Detectar Desmatamento", command=self.process).grid(row=3, column=0, columnspan=2, pady=5)

        self.coord_text = tk.Text(root, height=10, width=40)
        self.coord_text.grid(row=4, column=0, columnspan=2, pady=5)

    def add_coord(self):
        try:
            lon = float(self.lon_entry.get())
            lat = float(self.lat_entry.get())
            self.coords.append((lat, lon))  # lat, lon para folium
            self.coord_text.insert(tk.END, f"({lon}, {lat})\n")
            self.lon_entry.delete(0, tk.END)
            self.lat_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erro", "Coordenadas inválidas.")

    def open_file(self, path):
        print(f"Abrindo arquivo {path} no navegador padrão...")
        if platform.system() == "Windows":
            os.system(f'start {path}')
        elif platform.system() == "Darwin":  # macOS
            os.system(f'open {path}')
        else:  # Linux
            os.system(f'xdg-open {path}')

    def process(self):
        if len(self.coords) < 3:
            messagebox.showwarning("Aviso", "Insira ao menos 3 coordenadas.")
            return

        if self.coords[0] != self.coords[-1]:
            self.coords.append(self.coords[0])

        lat_center = sum([p[0] for p in self.coords]) / len(self.coords)
        lon_center = sum([p[1] for p in self.coords]) / len(self.coords)

        print("Salvando mapa base...")
        m = folium.Map(location=[lat_center, lon_center], zoom_start=19,
                       tiles='http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google')
        folium.Polygon(locations=self.coords, color='blue', fill=False).add_to(m)
        m.save("temp_map.html")

        print("Configurando Selenium para captura de tela...")
        options = Options()
        options.headless = True  # Se quiser ver o navegador, mude para False
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(800, 800)

        file_url = "file://" + os.path.realpath("temp_map.html")
        print(f"Abrindo arquivo local no navegador: {file_url}")
        driver.get(file_url)
        time.sleep(3)  # Espera o mapa carregar

        screenshot_path = "screenshot.png"
        driver.save_screenshot(screenshot_path)
        driver.quit()
        print(f"Screenshot salva em {screenshot_path}")

        img = cv2.imread(screenshot_path)
        height, width = img.shape[:2]
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        mask_green = cv2.inRange(hsv, lower_green, upper_green)
        mask_non_green = cv2.bitwise_not(mask_green)

        contours, _ = cv2.findContours(mask_non_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        lats = [p[0] for p in self.coords]
        lons = [p[1] for p in self.coords]
        lat_min, lat_max = min(lats), max(lats)
        lon_min, lon_max = min(lons), max(lons)

        def pixel_to_latlon(x, y):
            lat = lat_max - (y / height) * (lat_max - lat_min)
            lon = lon_min + (x / width) * (lon_max - lon_min)
            return (lat, lon)

        print("Gerando mapa do resultado...")
        desmatamento_map = folium.Map(location=[lat_center, lon_center], zoom_start=19,
                                      tiles='http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google')
        folium.Polygon(locations=self.coords, color='blue', fill=False).add_to(desmatamento_map)

        areas = []
        for cnt in contours:
            area_px = cv2.contourArea(cnt)
            if area_px > 100:
                approx = cv2.approxPolyDP(cnt, 3, True)
                poly_latlon = [pixel_to_latlon(p[0][0], p[0][1]) for p in approx]
                folium.Polygon(locations=poly_latlon, color='red', fill=False).add_to(desmatamento_map)

                polygon = Polygon([(lon, lat) for lat, lon in poly_latlon])
                project = pyproj.Transformer.from_crs("epsg:4326", "epsg:3857", always_xy=True).transform
                polygon_proj = transform(project, polygon)
                area_m2 = polygon_proj.area
                area_km2 = area_m2 / 1e6
                areas.append(area_km2)

        total_area = sum(areas)
        print(f"Área total desmatada estimada: {total_area:.4f} km²")

        if total_area > 0:
            popup_text = f"⚠️ Possível área desmatada detectada!\nÁrea total estimada: {total_area:.4f} km²"
            folium.Marker(location=[lat_center, lon_center],
                          popup=popup_text,
                          icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')).add_to(desmatamento_map)

        resultado_html = "resultado_desmatamento.html"
        desmatamento_map.save(resultado_html)

        # Remover arquivos temporários com verificação
        for f in ["temp_map.html", screenshot_path]:
            if os.path.exists(f):
                os.remove(f)
                print(f"Arquivo temporário removido: {f}")

        # Abrir o arquivo resultante no navegador padrão
        self.open_file(resultado_html)


if __name__ == "__main__":
    root = tk.Tk()
    app = DesmatamentoApp(root)
    root.mainloop()
