import tkinter as tk
from tkinter import messagebox
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Polygon

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Análise de Área de Desmatamento")

        self.coords = []

        #aqui man, e as label e entrada
        tk.Label(root, text="Longitude:").grid(row=0, column=0)
        self.lon_entry = tk.Entry(root)
        self.lon_entry.grid(row=0, column=1)

        tk.Label(root, text="Latitude:").grid(row=1, column=0)
        self.lat_entry = tk.Entry(root)
        self.lat_entry.grid(row=1, column=1)

        #os botões
        tk.Button(root, text="Adicionar Coordenada", command=self.add_coord).grid(row=2, column=0, columnspan=2, pady=5)
        tk.Button(root, text="Finalizar e Calcular", command=self.process_polygon).grid(row=3, column=0, columnspan=2, pady=5)

        # area de visualizacao de coordenadas
        self.coord_text = tk.Text(root, height=10, width=40)
        self.coord_text.grid(row=4, column=0, columnspan=2, pady=5)

    def add_coord(self):
        try:
            lon = float(self.lon_entry.get())
            lat = float(self.lat_entry.get())
            self.coords.append((lon, lat))
            self.coord_text.insert(tk.END, f"({lon}, {lat})\n")
            self.lon_entry.delete(0, tk.END)
            self.lat_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erro", "Coordenadas inválidas. Use números.")

    def process_polygon(self):
        if len(self.coords) < 3:
            messagebox.showwarning("Aviso", "Insira ao menos 3 coordenadas.")
            return

       
        if self.coords[0] != self.coords[-1]:
            self.coords.append(self.coords[0])

        # cria GeoDataFrame
        polygon = Polygon(self.coords)
        gdf = gpd.GeoDataFrame([{'geometry': polygon, 'tipo': 'desmatamento'}], crs='EPSG:4326')

        #aqui zeca reprojeta para metrico
        gdf_metric = gdf.to_crs(epsg=3857)
        gdf_metric['area_m2'] = gdf_metric.geometry.area

        # moostra resultado em mestro quadrado 
        area = gdf_metric['area_m2'].values[0]
        messagebox.showinfo("Área Calculada", f"Área: {area:,.2f} m²")

        # plota e exibi essa djanba
        ax = gdf_metric.plot(edgecolor='darkred', facecolor='#e6b8af', alpha=0.7, figsize=(10, 10))
        ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
        plt.title("Área de Mata Desmatada - Amazônia")
        plt.axis('off')
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
