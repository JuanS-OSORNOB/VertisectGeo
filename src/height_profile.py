import numpy as np
from shapely.geometry import LineString
from scipy.interpolate import RegularGridInterpolator

class Heightprofile():
    def __init__(self, grd_file, start_coords, end_coords):
        self.grd_file = grd_file
        self.start_coords = start_coords
        self.end_coords = end_coords

    @staticmethod
    def lon_to_km(lon):
        scale_factor = 111.0  #X coordinates, adjusting for variation in latitude
        lon_km = scale_factor * lon
        return lon_km
    
    @staticmethod
    def lat_to_km(lat):
        scale_factor = 111.0
        lat_km = scale_factor * lat #Y coordinates
        return lat_km
    
    @staticmethod
    def meters_to_km(depth):
        scale_factor = 1/1000
        depth_km = scale_factor * depth
        return depth_km
    
    def read_grd_ascii(self, file_path):
        """Reads the grd file.

        Args:
            file_path (_type_): Location of the file.

        Raises:
            ValueError: Not valid surface grid file.
            ValueError: Data size mismatch.

        Returns:
            _type_: x, y, data
        """
        with open(file_path, 'r') as f:
            # Read header
            header = f.readline().strip()
            if header != "DSAA":
                raise ValueError("Not a valid Surfer ASCII Grid file.")

            # Read grid dimensions
            nx, ny = map(int, f.readline().split())
            #print(f"Grid nx, ny = {nx, ny}")

            # Read coordinate bounds
            lon_min, lon_max = map(float, f.readline().split())
            lat_min, lat_max = map(float, f.readline().split())
            #print(f"Bounds coordinates (x-range), (y_range) = {lon_min, lon_max} {lat_min, lat_max}")
            # Read data range (not used in computation)
            zmin, zmax = map(float, f.readline().split())

            # Read grid data
            data = []
            for line in f:
                # Split each line into float values and append to the list
                data.extend(map(float, line.split()))
            # Check if the total number of values matches nx * ny
            if len(data) != nx * ny:
                raise ValueError("Data size mismatch: expected {}, got {}.".format(nx * ny, len(data)))

            # Reshape into 2D grid (row-major order)
            data = np.array(data).reshape((ny, nx))
            data_km = self.meters_to_km(data)

        # Create coordinates for grid
        lon_range = np.linspace(lon_min, lon_max, nx)
        lat_range = np.linspace(lat_min, lat_max, ny)
        return lon_range, lat_range, data_km
    
    def extract_profile(self, num_pts = 500):
        """_summary_

        Args:
            grd_file (_type_): _description_
            profile_name (_type_): _description_
            start_coords (_type_): _description_
            end_coords (_type_): _description_

        Returns:
            _type_: _description_
        """
        lon, lat, data_km = self.read_grd_ascii(self.grd_file)
        # Define the interpolator
        interpolator = RegularGridInterpolator((lat, lon), data_km, bounds_error=False, fill_value=np.nan)

        # Create a LineString and sample points along the line
        line = LineString([self.start_coords, self.end_coords])
        line_points = [line.interpolate(float(i) / num_pts, normalized=True).coords[0] for i in range(num_pts + 1)]

        # Extract elevations
        elevations = [interpolator((lat, lon)) for lon, lat in line_points]
        elevations = np.array(elevations)

        # Return distances and elevations
        distances = np.linspace(0, 111 * line.length, len(elevations))
        return distances, elevations