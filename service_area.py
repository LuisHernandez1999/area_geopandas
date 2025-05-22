import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx

# GeoJSON simulando área de desmatamento
geojson_data = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {"tipo": "desmatamento"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-53.1000, -4.0000],
                [-53.0950, -4.0000],
                [-53.0950, -4.0050],
                [-53.1000, -4.0050],
                [-53.1000, -4.0000]
            ]]
        }
    }]
}


gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])
gdf.set_crs(epsg=4326, inplace=True)  


gdf_metric = gdf.to_crs(epsg=3857)


gdf_metric['area_m2'] = gdf_metric.geometry.area


print(f"area da poligonal em metros quadrados: {gdf_metric['area_m2'].values[0]:,.2f} m²")


ax = gdf_metric.plot(
    edgecolor='darkred',
    facecolor='#e6b8af',
    alpha=0.7,
    figsize=(10, 10)
)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)
plt.title("area de mata desmatada amazonia")
plt.axis('off')
plt.show()
