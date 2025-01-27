import numpy as np
from shapely.geometry import LineString
from scipy.interpolate import RegularGridInterpolator

class Heightprofile():
    def __init__(self, grd_file, start_coords, end_coords):
        self.grd_file = grd_file
        self.start_coords = start_coords
        self.end_coords = end_coords

    def coordinates_to_km(self, lon, lat):
        lon_to_km = 111.0 * np.cos(np.radians(lat)) #X coordinates, adjusting for variation in latitude
        lat_to_km = 111.0 #Y coordinates
        return lon_to_km, lat_to_km
    
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

            # Read coordinate bounds
            xmin, xmax = map(float, f.readline().split())
            ymin, ymax = map(float, f.readline().split())

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

        # Create coordinates for grid
        x = np.linspace(xmin, xmax, nx)
        y = np.linspace(ymin, ymax, ny)
        return x, y, data
    
    def extract_profile(self):
        """_summary_

        Args:
            grd_file (_type_): _description_
            profile_name (_type_): _description_
            start_coords (_type_): _description_
            end_coords (_type_): _description_

        Returns:
            _type_: _description_
        """
        x, y, data = self.read_grd_ascii(self.grd_file)

        # Define the interpolator
        interpolator = RegularGridInterpolator((y, x), data, bounds_error=False, fill_value=np.nan)

        # Create a LineString and sample points along the line
        line = LineString([self.start_coords, self.end_coords])
        num_points = 500  # Number of points along the profile
        line_points = [line.interpolate(float(i) / num_points, normalized=True).coords[0] for i in range(num_points + 1)]

        # Extract elevations
        elevations = [interpolator((lat, lon)) for lon, lat in line_points]

        # Return distances and elevations
        distances = np.linspace(0, line.length, len(elevations))
        return distances, elevations