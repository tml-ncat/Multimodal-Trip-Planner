# Multimodal Trip Planner

A Plotly and Dash interface to show route geometry and travel itinerary details for different transport modes, built on the `r5py` library (Fink et al., 2022).

## Libraries needed
1. Pandas
2. Numpy
3. r5py
4. Geopandas
5. Dash/Plotly

## Quickstart

1. **Clone the Trip Planner repository**
```bash
git clone https://github.com/tml-ncat/Multimodal-Trip-Planner.git
cd Multimodal-Trip-Planner
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

3. **Install dependencies**
```bash
pip install --upgrade pip
pip install r5py pandas numpy geopandas dash plotly
```

**Note:** `r5py` requires a Java Development Kit (JDK). If `r5py` fails to initialize, install a JDK and ensure Java is available on your system PATH.

4. **Run the application**
```bash
cd src/main
python app.py
```

After running `python app.py`, open your browser and navigate to:
`http://127.0.0.1:8050/`

## Usage

1. **Launch the application**
   - After running `python app.py`, open `http://127.0.0.1:8050/`

2. **Input your travel details**
   - Set the origin and destination
   - Select the transport mode
   - View the detailed itinerary and route on the map

## Data requirements (inputs)

This app uses real network and transit inputs. What you need depends on which modes you want to run.

### Required for walk, bike, drive routing
1. **OSM extract** (roads and paths)
   - Recommended format: `.osm.pbf`
   - Common source: Geofabrik regional extracts, or a smaller bounding box extract

### Required for transit routing
2. **GTFS feed** (static schedule)
   - Needed to enable public transit itineraries
   - Common sources:
     - Transit agency GTFS download page (developer/open data portal)
     - Transitland feed listings
     - Mobility Database (GTFS registry)

### Optional for slope warnings
3. **DEM elevation raster**
   - GeoTIFF DEM (elevation) covering the area of interest
   - Common source: USGS 3DEP / The National Map

## Example dataset (Durham, North Carolina)

This project has been tested using the Durham, NC area.

General guidance:
- Use a Durham area GTFS feed
- Use an OSM extract that includes Durham and surrounding connections
- Optionally add a Durham area DEM GeoTIFF to enable slope warnings

## Where to place data (recommended folder layout)

Because data files can be large, store them outside the code directory in a local `data/` folder.

Example:
```
Multimodal-Trip-Planner/
  data/
    gtfs/
      durham_gtfs.zip
    osm/
      region.osm.pbf
    dem/
      durham_dem.tif
  src/
    main/
      app.py
  images/
```

**Important:**
- If your app uses hardcoded paths, update the data file paths inside `src/main/app.py` to point to your local files.
- If your app reads from a config file or environment variables, set them to match your data locations.

## What outputs does it produce?

The tool produces on-screen outputs in the interface, including:
- Route geometry displayed on the map
- Itinerary steps (walk, bike, drive, and transit legs when available)
- Summary statistics (for example: travel time, distance, and mode specific breakdowns)
- Slope warning indicators when elevation data is enabled

## Demo evidence

### Screenshots (relative paths)
These will render if the image files exist in your repo at the exact paths shown below.
GitHub paths are case-sensitive, so `images/3-transit.png` is different from `images/3-transit.PNG`.

![Example Image](images/3-transit.png)
![Example Image](images/2-bike.png)
![Example Image](images/1-shared.png)


### Demo videos
- https://youtube.com/shorts/p4yhmIHe61c?si=IswgtzuFk_VxY9QE
- https://youtu.be/7KgR7JX4FIc?si=DVt9lXw3NXHLcEJS
- https://youtube.com/shorts/laQQebEbygo?si=0hdmQWixw5YLOoZ4
- https://youtube.com/shorts/EqJQcEaSm_8?si=fzsFUy9wEO3MNdZZ

## Documentation
[R5py](https://r5py.readthedocs.io/en/stable/user-guide/user-manual/quickstart.html)

[Dash](https://dash.plotly.com/tutorial)

[Geopandas](https://geopandas.org/en/stable/docs.html)

## Features
- Interactive map to display routes
- Supports multiple transport modes (depends on GTFS and OSM coverage)
- Displays detailed travel statistics
- Responsive design for different devices

## Ongoing Work
1. Work with multiple user criteria (for example: bike level of traffic stress)
2.

## Note
For slope data, you need to download elevation data (GeoTIFF) for the location of interest. File sizes can be large and may not be suitable to store directly in the repository.

USGS download option: https://www.usgs.gov/tools/national-map-viewer

## Contributing

1. **Fork the repository**
   - Click the "Fork" button at the top-right of the repository page

2. **Clone your fork**
```bash
git clone <your-fork-url>
cd Multimodal-Trip-Planner
```

3. **Create a branch**
```bash
git checkout -b my-feature-branch
```

4. **Commit your changes**
```bash
git commit -am "Add new feature"
```

5. **Push your branch**
```bash
git push origin my-feature-branch
```

6. **Create a pull request**
   - Open your forked repository on GitHub and click "New pull request"

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Authorship
Primary developer: **Ridwan Tiamiyu**

## Acknowledgments
- Fink, C., Klumpenhouwer, W., Saraiva, M., Pereira, R., & Tenkanen, H. (2022). r5py: Rapid Realistic Routing with R5 in Python (0.0.4). Zenodo. https://doi.org/10.5281/zenodo.7060438
- Special thanks to C2SMARTER, Tier-1 UTC for providing funds for the project.
