import os
import cv2
import numpy as np
import folium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from shapely.geometry import Polygon
from shapely.ops import transform
import pyproj
import customtkinter as ctk
from tkinter import messagebox
import time
import platform


ctk.set_appearance_mode("dark")  
ctk.set_default_color_theme("blue")  

class DesmatamentoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌳 Detector de Desmatamento")
        self.root.geometry("600x750")
        
        self.coords = []
        
        
        main_frame = ctk.CTkFrame(root, corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🌳 DETECTOR DE DESMATAMENTO",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Análise inteligente de áreas florestais",
            font=ctk.CTkFont(size=14),
            text_color="gray70"
        )
        subtitle_label.pack(pady=(0, 30))
        
       
        coord_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        coord_frame.pack(fill="x", padx=20, pady=(0, 20))
        
       
        coord_title = ctk.CTkLabel(
            coord_frame,
            text="📍 COORDENADAS",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        coord_title.pack(pady=(15, 20))
        
       
        input_frame = ctk.CTkFrame(coord_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        
        lon_label = ctk.CTkLabel(
            input_frame,
            text="🌐 Longitude:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        lon_label.pack(anchor="w", pady=(0, 5))
        
        self.lon_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ex: -47.123456",
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.lon_entry.pack(fill="x", pady=(0, 15))
        
        
        lat_label = ctk.CTkLabel(
            input_frame,
            text="🗺️ Latitude:",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        lat_label.pack(anchor="w", pady=(0, 5))
        
        self.lat_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ex: -15.123456",
            font=ctk.CTkFont(size=12),
            height=35
        )
        self.lat_entry.pack(fill="x", pady=(0, 20))
        
        
        add_btn = ctk.CTkButton(
            coord_frame,
            text="➕ ADICIONAR COORDENADA",
            command=self.add_coord,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=40,
            fg_color="#27ae60",
            hover_color="#229954"
        )
        add_btn.pack(pady=(0, 20))
        
        
        list_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        
        list_title = ctk.CTkLabel(
            list_frame,
            text="📋 COORDENADAS ADICIONADAS",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        list_title.pack(pady=(15, 10))
        
        
        self.coord_counter = ctk.CTkLabel(
            list_frame,
            text="0 coordenadas",
            font=ctk.CTkFont(size=11),
            text_color="gray60"
        )
        self.coord_counter.pack(pady=(0, 15))
        
        
        self.coord_text = ctk.CTkTextbox(
            list_frame,
            height=120,
            font=ctk.CTkFont(family="Courier", size=10),
            corner_radius=8
        )
        self.coord_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Frame para botões de ação (primeira linha)
        action_frame1 = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame1.pack(fill="x", padx=20, pady=(0, 10))
        
        # Botão limpar coordenadas
        clear_btn = ctk.CTkButton(
            action_frame1,
            text="🗑️ LIMPAR",
            command=self.clear_coords,
            font=ctk.CTkFont(size=11, weight="bold"),
            height=35,
            width=120,
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        )
        clear_btn.pack(side="left", padx=(0, 10))
        
      
        map_btn = ctk.CTkButton(
            action_frame1,
            text="🗺️ GERAR MAPA",
            command=self.generate_map,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        map_btn.pack(side="right", fill="x", expand=True)
        
       
        action_frame2 = ctk.CTkFrame(main_frame, fg_color="transparent")
        action_frame2.pack(fill="x", padx=20, pady=(0, 10))
        
        process_btn = ctk.CTkButton(
            action_frame2,
            text="🔍 DETECTAR DESMATAMENTO",
            command=self.process,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=50,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        process_btn.pack(fill="x")
        
        
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="✅ Sistema pronto para uso",
            font=ctk.CTkFont(size=11),
            text_color="#27ae60"
        )
        self.status_label.pack(pady=(10, 20))
        
        
        self.progress_bar = ctk.CTkProgressBar(main_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=(0, 20))
        self.progress_bar.pack_forget()  

    def add_coord(self):
        try:
            lon = float(self.lon_entry.get())
            lat = float(self.lat_entry.get())
            

            if not (-180 <= lon <= 180) or not (-90 <= lat <= 90):
                raise ValueError("Coordenadas fora do intervalo válido")
            
            self.coords.append((lat, lon))  
            
            
            coord_text = f"📍 Ponto {len(self.coords)}: ({lon:.6f}, {lat:.6f})\n"
            self.coord_text.insert("end", coord_text)
            
           
            self.lon_entry.delete(0, "end")
            self.lat_entry.delete(0, "end")
            
           
            self.coord_counter.configure(text=f"{len(self.coords)} coordenadas")
            self.status_label.configure(
                text=f"✅ {len(self.coords)} coordenadas adicionadas",
                text_color="#27ae60"
            )
            
           
            self.lon_entry.focus()
            
        except ValueError as e:
            messagebox.showerror(
                "❌ Erro de Validação", 
                "Coordenadas inválidas!\n\n"
                "• Longitude: -180 a 180\n"
                "• Latitude: -90 a 90\n"
                "• Use apenas números"
            )
            self.status_label.configure(
                text="❌ Erro: coordenadas inválidas",
                text_color="#e74c3c"
            )

    def clear_coords(self):
  
        self.coords.clear()
        self.coord_text.delete("1.0", "end")
        self.coord_counter.configure(text="0 coordenadas")
        self.status_label.configure(
            text="🗑️ Coordenadas removidas",
            text_color="#f39c12"
        )

    def generate_map(self):
      
        if len(self.coords) < 3:
            messagebox.showwarning(
                "⚠️ Dados Insuficientes", 
                "É necessário inserir pelo menos 3 coordenadas\npara gerar o mapa da área."
            )
            self.status_label.configure(
                text="⚠️ Mínimo 3 coordenadas para gerar mapa",
                text_color="#f39c12"
            )
            return

        try:
            self.status_label.configure(
                text="🗺️ Gerando mapa da área...",
                text_color="#3498db"
            )
            self.root.update()


            coords_for_map = self.coords.copy()
            

            if coords_for_map[0] != coords_for_map[-1]:
                coords_for_map.append(coords_for_map[0])


            lat_center = sum([p[0] for p in coords_for_map]) / len(coords_for_map)
            lon_center = sum([p[1] for p in coords_for_map]) / len(coords_for_map)


            print("Gerando mapa da área selecionada...")
            area_map = folium.Map(
                location=[lat_center, lon_center], 
                zoom_start=15,
                tiles='http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', 
                attr='Google Satellite'
            )
            

            folium.Polygon(
                locations=coords_for_map, 
                color='blue', 
                weight=3,
                fill=True,
                fillColor='blue',
                fillOpacity=0.2,
                popup=f"Área selecionada\n{len(self.coords)} pontos"
            ).add_to(area_map)
            

            for i, (lat, lon) in enumerate(self.coords, 1):
                folium.Marker(
                    location=[lat, lon],
                    popup=f"Ponto {i}\nLat: {lat:.6f}\nLon: {lon:.6f}",
                    icon=folium.Icon(color='blue', icon='info-sign')
                ).add_to(area_map)
            

            folium.Marker(
                location=[lat_center, lon_center],
                popup=f"Centro da área\nLat: {lat_center:.6f}\nLon: {lon_center:.6f}",
                icon=folium.Icon(color='green', icon='star')
            ).add_to(area_map)


            mapa_html = "mapa_area_selecionada.html"
            area_map.save(mapa_html)


            self.status_label.configure(
                text="✅ Mapa gerado com sucesso!",
                text_color="#27ae60"
            )


            messagebox.showinfo(
                "🗺️ Mapa Gerado",
                f"Mapa da área criado com sucesso!\n\n"
                f"📍 Pontos marcados: {len(self.coords)}\n"
                f"🎯 Centro: ({lat_center:.6f}, {lon_center:.6f})\n\n"
                f"O mapa será aberto no navegador."
            )


            self.open_file(mapa_html)

        except Exception as e:
            messagebox.showerror(
                "❌ Erro ao Gerar Mapa",
                f"Ocorreu um erro ao gerar o mapa:\n\n{str(e)}"
            )
            self.status_label.configure(
                text="❌ Erro ao gerar mapa",
                text_color="#e74c3c"
            )

    def update_progress(self, value, text):

        self.progress_bar.set(value)
        self.status_label.configure(text=text, text_color="#3498db")
        self.root.update()

    def open_file(self, path):
        print(f"Abrindo arquivo {path} no navegador padrão...")
        if platform.system() == "Windows":
            os.system(f'start {path}')
        elif platform.system() == "Darwin":  
            os.system(f'open {path}')
        else: 
            os.system(f'xdg-open {path}')

    def process(self):
        if len(self.coords) < 3:
            messagebox.showwarning(
                "⚠️ Dados Insuficientes", 
                "É necessário inserir pelo menos 3 coordenadas\npara formar uma área de análise."
            )
            self.status_label.configure(
                text="⚠️ Mínimo 3 coordenadas necessárias",
                text_color="#f39c12"
            )
            return


        self.progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        
        try:

            self.update_progress(0.1, "🔄 Preparando análise...")
            
            if self.coords[0] != self.coords[-1]:
                self.coords.append(self.coords[0])

            lat_center = sum([p[0] for p in self.coords]) / len(self.coords)
            lon_center = sum([p[1] for p in self.coords]) / len(self.coords)


            self.update_progress(0.2, "🗺️ Gerando mapa base...")
            print("Salvando mapa base...")
            m = folium.Map(location=[lat_center, lon_center], zoom_start=19,
                           tiles='http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}', attr='Google')
            folium.Polygon(locations=self.coords, color='blue', fill=False).add_to(m)
            m.save("temp_map.html")

           
            self.update_progress(0.4, "📸 Configurando captura de imagem...")
            print("Configurando Selenium para captura de tela...")
            options = Options()
            options.headless = True
            driver = webdriver.Chrome(options=options)
            driver.set_window_size(800, 800)


            self.update_progress(0.6, "📷 Capturando imagem satelital...")
            file_url = "file://" + os.path.realpath("temp_map.html")
            print(f"Abrindo arquivo local no navegador: {file_url}")
            driver.get(file_url)
            time.sleep(3)

            screenshot_path = "screenshot.png"
            driver.save_screenshot(screenshot_path)
            driver.quit()
            print(f"Screenshot salva em {screenshot_path}")


            self.update_progress(0.8, "🔍 Analisando vegetação...")
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


            self.update_progress(0.9, "📊 Gerando relatório...")
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


            self.update_progress(1.0, "✅ Análise concluída!")

            if total_area > 0:
                popup_text = f"⚠️ Possível área desmatada detectada!\nÁrea total estimada: {total_area:.4f} km²"
                folium.Marker(location=[lat_center, lon_center],
                              popup=popup_text,
                              icon=folium.Icon(color='red', icon='exclamation-triangle', prefix='fa')).add_to(desmatamento_map)
                
                self.status_label.configure(
                    text=f"⚠️ Desmatamento detectado: {total_area:.4f} km²",
                    text_color="#e74c3c"
                )
                

                messagebox.showwarning(
                    "⚠️ Alerta de Desmatamento",
                    f"Possível área desmatada detectada!\n\n"
                    f"📊 Área estimada: {total_area:.4f} km²\n"
                    f"📍 Coordenadas analisadas: {len(self.coords)-1}\n\n"
                    f"O relatório detalhado será aberto no navegador."
                )
            else:
                self.status_label.configure(
                    text="✅ Nenhum desmatamento detectado na área",
                    text_color="#27ae60"
                )
                
                messagebox.showinfo(
                    "✅ Resultado da Análise",
                    f"Análise concluída com sucesso!\n\n"
                    f"🌳 Nenhum desmatamento detectado\n"
                    f"📍 Coordenadas analisadas: {len(self.coords)-1}\n\n"
                    f"A área analisada apresenta cobertura vegetal adequada."
                )

            resultado_html = "resultado_desmatamento.html"
            desmatamento_map.save(resultado_html)


            for f in ["temp_map.html", screenshot_path]:
                if os.path.exists(f):
                    os.remove(f)
                    print(f"Arquivo temporário removido: {f}")


            self.open_file(resultado_html)
            
        except Exception as e:
            messagebox.showerror(
                "❌ Erro no Processamento",
                f"Ocorreu um erro durante a análise:\n\n{str(e)}\n\n"
                f"Verifique se o ChromeDriver está instalado\ne se as coordenadas são válidas."
            )
            self.status_label.configure(
                text="❌ Erro no processamento",
                text_color="#e74c3c"
            )
        
        finally:

            self.progress_bar.pack_forget()


if __name__ == "__main__":
    root = ctk.CTk()
    app = DesmatamentoApp(root)
    root.mainloop()