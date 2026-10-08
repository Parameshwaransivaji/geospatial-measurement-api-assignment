import tempfile
import os
import zipfile
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString

def process_geospatial_file(file_bytes: bytes, filename: str):
    ext = os.path.splitext(filename)[1].lower()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = os.path.join(tmpdir, filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
            
        # Shapefile (.zip) அல்லது KML-ஐ pyogrio மூலம் படித்தல்
        if ext == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)
            shp_files = [f for f in os.listdir(tmpdir) if f.endswith('.shp')]
            if not shp_files:
                raise ValueError("No .shp file found inside zip")
            gdf = gpd.read_file(os.path.join(tmpdir, shp_files[0]), engine="pyogrio")
        elif ext == '.kml':
            gdf = gpd.read_file(file_path, engine="pyogrio")
        else:
            raise ValueError("Unsupported file format. Use .zip or .kml")

        crs_str = str(gdf.crs) if gdf.crs else "EPSG:4326"
        
        # CRS Projection (Meters/Sq meters கணக்கிட)
        gdf_projected = gdf.copy()
        if gdf_projected.crs is None or gdf_projected.crs.is_geographic:
            try:
                utm_crs = gdf_projected.estimate_utm_crs()
                gdf_projected = gdf_projected.to_crs(utm_crs)
            except Exception:
                gdf_projected = gdf_projected.to_crs("EPSG:3857")

        features_info = []
        measurements = []

        for idx, row in gdf.iterrows():
            geom = row.geometry
            proj_geom = gdf_projected.geometry.iloc[idx] if idx < len(gdf_projected) else None
            geom_type = geom.geom_type if geom else "Unknown"
            properties = {k: str(v) for k, v in row.items() if k != 'geometry'}

            features_info.append({
                "feature_id": idx,
                "geometry_type": geom_type,
                "crs": crs_str,
                "properties": properties
            })

            meas = {"feature_id": idx, "geometry_type": geom_type, "area_sq_m": None, "length_m": None}
            
            if proj_geom:
                if isinstance(proj_geom, (Polygon, MultiPolygon)):
                    meas["area_sq_m"] = round(proj_geom.area, 2)
                elif isinstance(proj_geom, (LineString, MultiLineString)):
                    meas["length_m"] = round(proj_geom.length, 2)

            measurements.append(meas)

        return {
            "filename": filename,
            "feature_count": len(gdf),
            "crs": crs_str,
            "features": features_info,
            "measurements": measurements
        }
