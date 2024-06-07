from dash import Dash, html, dcc, Input, Output, State, callback_context, no_update
import plotly.graph_objs as go
import geopandas as gpd
from shapely.geometry import Point
import r5py
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd

app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

gtfs_path = 'gtfs.zip'
osm_path = 'durham_new.osm.pbf'
transport_network = r5py.TransportNetwork(osm_path, [gtfs_path])

# Setup a clickable map
lat_start, lat_end = 35.88, 36.08
lon_start, lon_end = -78.98, -78.85
lat_points = np.linspace(lat_start, lat_end, 50)
lon_points = np.linspace(lon_start, lon_end, 50)
lat, lon = np.meshgrid(lat_points, lon_points)
lat = lat.flatten()
lon = lon.flatten()

fig = go.Figure(go.Scattermapbox(
    mode='markers',
    lon=lon,
    lat=lat,
    marker={'size': 5, 'opacity': 0},
    hoverinfo='none',
    showlegend=False
))

fig.update_layout(
    mapbox={
        'style': "carto-positron",
        'center': {'lat': 35.9940, 'lon': -78.8986},
        'zoom': 10
    },
    margin={'l': 0, 'r': 0, 'b': 0, 't': 0},
    clickmode='event+select'
)

hours_options = [{'label': f'{i:02d}', 'value': f'{i:02d}'} for i in range(24)]
minutes_options = [{'label': f'{i:02d}', 'value': f'{i:02d}'} for i in range(0, 60, 5)]
optimization_options = [
    {'label': 'Total Time', 'value': 'total_time'},
    {'label': 'Number of Transfers', 'value': 'transfers'},
    {'label': 'Wait Time', 'value': 'wait_time'},
    {'label': 'Walking Time', 'value': 'walking_time'}
]

app.layout = html.Div(style={'backgroundColor': '#ffffff', 'boxSizing': 'border-box', 'padding': '10px'}, children=[
    html.Div([
        html.H1("Trip Planner", style={'textAlign': 'center', 'color': '#333333', 'padding': '10px', 'background-color': '#f4f4f9'}),
    ], style={'width': '100%', 'display': 'block'}),
    html.Div([
        html.Div([
            html.Label('Enter your origin (lat, lon):', style={'margin': '5px', 'color': '#555555'}),
            dcc.Input(id='input-origin', type='text', placeholder='Enter origin lat, lon', style={'width': '100%', 'margin': '5px'}),
            html.Label('Enter your destination (lat, lon):', style={'margin': '5px', 'color': '#555555'}),
            dcc.Input(id='input-destination', type='text', placeholder='Enter destination lat, lon', style={'width': '100%', 'margin': '5px'}),
            html.Label('Departure Time:', style={'margin': '5px', 'color': '#555555'}),
            dcc.RadioItems(
                id='departure-time-radio',
                options=[
                    {'label': 'Leave Now', 'value': 'now'},
                    {'label': 'Choose Time', 'value': 'future'}
                ],
                value='now',
                labelStyle={'display': 'inline-block', 'margin': '5px'}
            ),
            html.Div(id='departure-time-div', children=[
                dcc.DatePickerSingle(
                    id='departure-date-picker',
                    min_date_allowed=date.today(),
                    initial_visible_month=date.today(),
                    date=date.today(),
                    style={'margin': '5px'}
                ),
                html.Div([
                    dcc.Dropdown(id='departure-hour', options=hours_options, placeholder='Hour', style={'width': '48%', 'display': 'inline-block', 'margin': '5px'}),
                    dcc.Dropdown(id='departure-minute', options=minutes_options, placeholder='Minute', style={'width': '48%', 'display': 'inline-block', 'margin': '5px'})
                ])
            ], style={'display': 'none'}),
            html.Label('Optimization Criteria:', style={'margin': '5px', 'color': '#555555'}),
            dcc.Dropdown(id='optimization-criteria', options=optimization_options, value='total_time', style={'margin': '5px'}),
            html.Button('Calculate Travel Time', id='calculate-button', n_clicks=0, style={'margin': '5px', 'background-color': '#74bf0c', 'color': 'black', 'font-weight': 'bold'}),
            html.Button('Start Over', id='start-over-button', n_clicks=0, style={'margin': '5px', 'background-color': '#D9534F', 'color': 'white', 'font-weight': 'bold'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '20px', 'background-color': '#eaeaea', 'boxSizing': 'border-box'}),
        html.Div([
            html.Label('Select your transport mode:', style={'margin': '5px', 'color': '#555555'}),
            html.Div([
                html.Button('Transit 🚌', id='mode-transit', n_clicks=0, style={'margin': '5px', 'background-color': '#93979C', 'color': 'white'}),
                html.Button('Car 🚗', id='mode-car', n_clicks=0, style={'margin': '5px', 'background-color': '#93979C', 'color': 'white'}),
                html.Button('Bike 🚲', id='mode-bike', n_clicks=0, style={'margin': '5px', 'background-color': '#93979C', 'color': 'white'}),
                html.Button('Shared Ride 🚕', id='mode-shared-ride', n_clicks=0, style={'margin': '5px', 'background-color': '#93979C', 'color': 'white'}),
                html.Button('Walk 🚶🏻', id='mode-walk', n_clicks=0, style={'margin': '5px', 'background-color': '#93979C', 'color': 'white'}),
            ], style={'display': 'flex', 'flex-wrap': 'wrap'}),
            html.Div(id='travel-time', style={'padding': '10px', 'background-color': '#f4f4f9', 'color': '#333333', 'text-align': 'center'})
        ], style={'width': '50%', 'display': 'inline-block', 'padding': '20px', 'background-color': '#eaeaea', 'boxSizing': 'border-box'}),
    ], id='main-content', style={'display': 'flex', 'flex-wrap': 'wrap', 'height': 'auto', 'boxSizing': 'border-box'}),
    html.Div([
        dcc.Graph(id='map-graph', figure=fig, style={'height': '80vh', 'width': '100%'})
    ], style={'width': '100%', 'display': 'block', 'boxSizing': 'border-box'}),
])

@app.callback(
    [Output('input-origin', 'value'),
     Output('input-destination', 'value'),
     Output('map-graph', 'figure'),
     Output('travel-time', 'children'),
     Output('mode-transit', 'style'),
     Output('mode-car', 'style'),
     Output('mode-bike', 'style'),
     Output('mode-shared-ride', 'style'),
     Output('mode-walk', 'style')],
    [Input('map-graph', 'clickData'),
     Input('calculate-button', 'n_clicks'),
     Input('start-over-button', 'n_clicks'),
     Input('mode-transit', 'n_clicks'),
     Input('mode-car', 'n_clicks'),
     Input('mode-bike', 'n_clicks'),
     Input('mode-shared-ride', 'n_clicks'),
     Input('mode-walk', 'n_clicks'),
     Input('optimization-criteria', 'value')],
    [State('input-origin', 'value'),
     State('input-destination', 'value'),
     State('mode-transit', 'n_clicks'),
     State('mode-car', 'n_clicks'),
     State('mode-bike', 'n_clicks'),
     State('mode-shared-ride', 'n_clicks'),
     State('mode-walk', 'n_clicks'),
     State('departure-time-radio', 'value'),
     State('departure-date-picker', 'date'),
     State('departure-hour', 'value'),
     State('departure-minute', 'value'),
     State('map-graph', 'figure')]
)
def update_inputs_and_calculate_travel_time(clickData, n_clicks, start_over_clicks, transit_clicks, car_clicks, bike_clicks, shared_ride_clicks, walk_clicks, optimization_criteria, origin, destination, transit_clicks_state, car_clicks_state, bike_clicks_state, shared_ride_clicks_state, walk_clicks_state, departure_time_radio, departure_date, departure_hour, departure_minute, current_figure):
    ctx = callback_context
    if not ctx.triggered:
        return origin, destination, current_figure, html.Div("Enter valid coordinates and click 'Calculate Travel Time'.", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'}), {'margin': '5px', 'background-color': '#93979C', 'color': 'white'}, {'margin': '5px', 'background-color': '#93979C', 'color': 'white'}, {'margin': '5px', 'background-color': '#93979C', 'color': 'white'}, {'margin': '5px', 'background-color': '#93979C', 'color': 'white'}, {'margin': '5px', 'background-color': '#93979C', 'color': 'white'}

    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    # Determine the selected mode based on button clicks
    mode_styles = {
        'mode-transit': {'margin': '5px', 'background-color': '#93979C', 'color': 'white'},
        'mode-car': {'margin': '5px', 'background-color': '#93979C', 'color': 'white'},
        'mode-bike': {'margin': '5px', 'background-color': '#93979C', 'color': 'white'},
        'mode-shared-ride': {'margin': '5px', 'background-color': '#93979C', 'color': 'white'},
        'mode-walk': {'margin': '5px', 'background-color': '#93979C', 'color': 'white'}
    }

    mode_of_travel = 'TRANSIT'  # Default to transit if none selected
    if trigger == 'mode-car':
        mode_of_travel = 'CAR'
    elif trigger == 'mode-bike':
        mode_of_travel = 'BICYCLE'
    elif trigger == 'mode-transit':
        mode_of_travel = 'TRANSIT'
    elif trigger == 'mode-shared-ride':
        mode_of_travel = 'SHARED_RIDE'
    elif trigger == 'mode-walk':
        mode_of_travel = 'WALK'
    elif trigger == 'calculate-button':
        # Use the last selected mode when Calculate Travel Time button is clicked
        if car_clicks_state >= bike_clicks_state and car_clicks_state >= transit_clicks_state and car_clicks_state >= shared_ride_clicks_state and car_clicks_state >= walk_clicks_state:
            mode_of_travel = 'CAR'
        elif bike_clicks_state >= car_clicks_state and bike_clicks_state >= transit_clicks_state and bike_clicks_state >= shared_ride_clicks_state and bike_clicks_state >= walk_clicks_state:
            mode_of_travel = 'BICYCLE'
        elif transit_clicks_state >= car_clicks_state and transit_clicks_state >= bike_clicks_state and transit_clicks_state >= shared_ride_clicks_state and transit_clicks_state >= walk_clicks_state:
            mode_of_travel = 'TRANSIT'
        elif shared_ride_clicks_state >= car_clicks_state and shared_ride_clicks_state >= bike_clicks_state and shared_ride_clicks_state >= transit_clicks_state and shared_ride_clicks_state >= walk_clicks_state:
            mode_of_travel = 'SHARED_RIDE'
        elif walk_clicks_state >= car_clicks_state and walk_clicks_state >= bike_clicks_state and walk_clicks_state >= transit_clicks_state and walk_clicks_state >= shared_ride_clicks_state:
            mode_of_travel = 'WALK'
    elif trigger == 'start-over-button':
        return '', '', fig, '', mode_styles['mode-transit'], mode_styles['mode-car'], mode_styles['mode-bike'], mode_styles['mode-shared-ride'], mode_styles['mode-walk']

    if trigger == 'map-graph':
        coords = clickData['points'][0]
        lat, lon = coords['lat'], coords['lon']
        coords_str = f"{lat}, {lon}"

        if not origin:
            new_figure = go.Figure(data=current_figure['data'], layout=current_figure['layout'])
            new_figure.add_trace(go.Scattermapbox(
                mode='markers+text',
                lon=[lon],
                lat=[lat],
                marker={'size': 10, 'color': 'red'},
                text=["Origin"],
                textposition="bottom right",
                showlegend=False
            ))
            return coords_str, destination, new_figure, no_update, mode_styles['mode-transit'], mode_styles['mode-car'], mode_styles['mode-bike'], mode_styles['mode-shared-ride'], mode_styles['mode-walk']
        elif not destination:
            new_figure = go.Figure(data=current_figure['data'], layout=current_figure['layout'])
            new_figure.add_trace(go.Scattermapbox(
                mode='markers+text',
                lon=[float(origin.split(',')[1]), lon],
                lat=[float(origin.split(',')[0]), lat],
                marker={'size': 10, 'color': ['red', '#93979C']},
                text=["Origin", "Destination"],
                textposition="bottom right",
                showlegend=False
            ))
            return origin, coords_str, new_figure, no_update, mode_styles['mode-transit'], mode_styles['mode-car'], mode_styles['mode-bike'], mode_styles['mode-shared-ride'], mode_styles['mode-walk']
        else:
            new_figure = go.Figure(data=current_figure['data'], layout=current_figure['layout'])
            new_figure.add_trace(go.Scattermapbox(
                mode='markers+text',
                lon=[lon],
                lat=[lat],
                marker={'size': 10, 'color': '#93979C'},
                text=["Origin"],
                textposition="bottom right",
                showlegend=False
            ))
            return coords_str, None, new_figure, no_update, mode_styles['mode-transit'], mode_styles['mode-car'], mode_styles['mode-bike'], mode_styles['mode-shared-ride'], mode_styles['mode-walk']

    if trigger in ['calculate-button', 'mode-transit', 'mode-car', 'mode-bike', 'mode-shared-ride', 'mode-walk', 'optimization-criteria'] and n_clicks > 0 and origin and destination:
        try:
            origin_lat, origin_lon = map(float, origin.split(','))
            destination_lat, destination_lon = map(float, destination.split(','))
            origin_point = Point(origin_lon, origin_lat)
            destination_point = Point(destination_lon, destination_lat)
            origins = gpd.GeoDataFrame([{'id': 'origin', 'geometry': origin_point}], crs="EPSG:4326")
            destinations = gpd.GeoDataFrame([{'id': 'destination', 'geometry': destination_point}], crs="EPSG:4326")

            if departure_time_radio == 'future' and departure_date and departure_hour and departure_minute:
                departure_datetime = datetime.combine(datetime.fromisoformat(departure_date).date(), datetime.strptime(f'{departure_hour}:{departure_minute}', '%H:%M').time())
            else:
                departure_datetime = datetime.now()

            if mode_of_travel == 'SHARED_RIDE':
                # Compute car travel time
                car_itineraries_computer = r5py.DetailedItinerariesComputer(
                    transport_network,
                    origins=origins,
                    destinations=destinations,
                    departure=departure_datetime,
                    transport_modes=['CAR']
                )
                car_travel_details = car_itineraries_computer.compute_travel_details()
                min_car_travel_time = car_travel_details['travel_time'].min()

                # Calculate additional wait time (normally distributed)
                wait_time = np.random.normal(loc=8, scale=3)
                wait_time = max(1, min(15, wait_time))  # Bound wait time between 1 and 15

                # Calculate additional travel time (exponentially distributed)
                additional_travel_time = np.random.exponential(scale=2)
                additional_travel_time = max(1, min(8, additional_travel_time))  # Bound additional travel time between 1 and 8

                total_travel_time_seconds = min_car_travel_time.total_seconds() + wait_time * 60 + additional_travel_time * 60
                hours = int(total_travel_time_seconds // 3600)
                minutes = int((total_travel_time_seconds % 3600) // 60)
                seconds = int(total_travel_time_seconds % 60)

                wait_minutes = int(wait_time)
                wait_seconds = int((wait_time - wait_minutes) * 60)

                additional_minutes = int(additional_travel_time)
                additional_seconds = int((additional_travel_time - additional_minutes) * 60)

                base_travel_minutes = int(min_car_travel_time.total_seconds() // 60)
                base_travel_seconds = int(min_car_travel_time.total_seconds() % 60)

                output = [
                    html.Div(f"Calculated Shared Ride Travel Time: {hours} hours, {minutes} minutes, and {seconds} seconds", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'}),
                    html.Div(f"Wait Time: {wait_minutes} minutes, {wait_seconds} seconds", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'}),
                    html.Div(f"Additional Travel Time: {additional_minutes} minutes, {additional_seconds} seconds", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'}),
                    html.Div(f"Base Travel Time: {base_travel_minutes} minutes, {base_travel_seconds} seconds", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'})
                ]

                mode_styles['mode-shared-ride']['background-color'] = '#74bf0c'
                mode_styles['mode-shared-ride']['color'] = 'black'

                # Convert current_figure to go.Figure if it's a dict
                if isinstance(current_figure, dict):
                    current_figure = go.Figure(current_figure)

                # Clear existing route traces
                current_figure.data = []

                # Use the car route for shared ride
                route_geometry = car_travel_details.loc[car_travel_details['travel_time'] == min_car_travel_time, 'geometry']
                if not route_geometry.empty:
                    route_coords = list(route_geometry.values[0].coords)
                    route_lons = [coord[0] for coord in route_coords]
                    route_lats = [coord[1] for coord in route_coords]

                    route_trace = go.Scattermapbox(
                        mode='lines',
                        lon=route_lons,
                        lat=route_lats,
                        line=dict(width=2, color='blue'),
                        name='Route'
                    )
                    current_figure.add_trace(route_trace)

                # Add origin and destination markers back if they were removed
                current_figure.add_trace(go.Scattermapbox(
                    mode='markers+text',
                    lon=[origin_lon, destination_lon],
                    lat=[origin_lat, destination_lat],
                    marker={'size': 10, 'color': ['red', '#93979C']},
                    text=["Origin", "Destination"],
                    textposition="bottom right",
                    showlegend=False
                ))

                return origin, destination, current_figure, output, mode_styles['mode-transit'], mode_styles['mode-car'], mode_styles['mode-bike'], mode_styles['mode-shared-ride'], mode_styles['mode-walk']

            detailed_itineraries_computer = r5py.DetailedItinerariesComputer(
                transport_network,
                origins=origins,
                destinations=destinations,
                departure=departure_datetime,
                transport_modes=[mode_of_travel]
            )
            travel_details = detailed_itineraries_computer.compute_travel_details()

            # Convert current_figure to go.Figure if it's a dict
            if isinstance(current_figure, dict):
                current_figure = go.Figure(current_figure)

            # Clear existing route traces
            current_figure.data = []

            route_trace = None

            # Conversion functions
            def meters_to_miles(meters):
                return meters * 0.000621371

            if mode_of_travel == 'TRANSIT':
                # Group by option and calculate the total travel time
                travel_details['total_time'] = travel_details['travel_time'] + travel_details['wait_time']

                # Calculate walking time as the sum of the first and last segment travel times
                walking_time = travel_details.groupby('option', group_keys=False).apply(lambda x: x.iloc[0]['travel_time'] + x.iloc[-1]['travel_time']).reset_index(name='walking_time')

                # Calculate the number of transfers
                travel_details['num_transfers'] = travel_details.groupby('option')['segment'].transform('count') - 3

                grouped_travel_details = travel_details.groupby('option').agg(
                    total_time=('total_time', 'sum'),
                    wait_time=('wait_time', 'sum'),
                    num_transfers=('num_transfers', 'first'),
                    distance=('distance', 'sum')
                ).reset_index().merge(walking_time, on='option')

                # Select the best option based on the selected optimization criteria
                if optimization_criteria == 'total_time':
                    min_travel_time_option = grouped_travel_details.loc[grouped_travel_details['total_time'].idxmin()]
                elif optimization_criteria == 'transfers':
                    min_travel_time_option = grouped_travel_details.loc[grouped_travel_details['num_transfers'].idxmin()]
                elif optimization_criteria == 'wait_time':
                    min_travel_time_option = grouped_travel_details.loc[grouped_travel_details['wait_time'].idxmin()]
                elif optimization_criteria == 'walking_time':
                    min_travel_time_option = grouped_travel_details.loc[grouped_travel_details['walking_time'].idxmin()]
                else:
                    min_travel_time_option = grouped_travel_details.loc[grouped_travel_details['total_time'].idxmin()]

                selected_option_details = travel_details[travel_details['option'] == min_travel_time_option['option']]

                # Calculate total travel time for the selected option
                total_travel_time_seconds = selected_option_details['total_time'].sum().total_seconds()
                total_wait_time_seconds = selected_option_details['wait_time'].sum().total_seconds()
                total_time_seconds = total_travel_time_seconds + total_wait_time_seconds

                total_distance_meters = selected_option_details['distance'].sum()
                total_distance_miles = meters_to_miles(total_distance_meters)

                first_row = selected_option_details.iloc[0]
                last_row = selected_option_details.iloc[-1]
                total_walking_distance_meters = first_row['distance'] + last_row['distance']
                total_walking_distance_miles = meters_to_miles(total_walking_distance_meters)
                total_walking_time = first_row['travel_time'] + last_row['travel_time']
                total_out_of_vehicle_time = total_walking_time + selected_option_details['wait_time'].sum()

                # Extract and plot the route geometry
                first_segment = selected_option_details.iloc[0]
                last_segment = selected_option_details.iloc[-1]
                transit_segments = selected_option_details.iloc[1:-1]

                first_segment_coords = list(first_segment['geometry'].coords)
                last_segment_coords = list(last_segment['geometry'].coords)
                transit_coords = [coord for segment in transit_segments['geometry'] for coord in segment.coords]

                first_segment_lons = [coord[0] for coord in first_segment_coords]
                first_segment_lats = [coord[1] for coord in first_segment_coords]
                last_segment_lons = [coord[0] for coord in last_segment_coords]
                last_segment_lats = [coord[1] for coord in last_segment_coords]
                transit_lons = [coord[0] for coord in transit_coords]
                transit_lats = [coord[1] for coord in transit_coords]

                first_segment_trace = go.Scattermapbox(
                    mode='lines',
                    lon=first_segment_lons,
                    lat=first_segment_lats,
                    line=dict(width=2, color='lightblue'),
                    name='First Walk Segment'
                )

                transit_trace = go.Scattermapbox(
                    mode='lines',
                    lon=transit_lons,
                    lat=transit_lats,
                    line=dict(width=2, color='blue'),
                    name='Transit Segment'
                )

                last_segment_trace = go.Scattermapbox(
                    mode='lines',
                    lon=last_segment_lons,
                    lat=last_segment_lats,
                    line=dict(width=2, color='lightblue'),
                    name='Last Walk Segment'
                )

                current_figure.add_trace(first_segment_trace)
                current_figure.add_trace(transit_trace)
                current_figure.add_trace(last_segment_trace)

                # Add origin and destination markers back if they were removed
                current_figure.add_trace(go.Scattermapbox(
                    mode='markers+text',
                    lon=[origin_lon, destination_lon],
                    lat=[origin_lat, destination_lat],
                    marker={'size': 10, 'color': ['red', '#93979C']},
                    text=["Origin", "Destination"],
                    textposition="bottom right",
                    showlegend=False
                ))

                hours = int(total_time_seconds // 3600)
                minutes = int((total_time_seconds % 3600) // 60)
                seconds = int(total_time_seconds % 60)

                output = [
                    html.Div(f"Calculated Travel Time: {hours} hours, {minutes} minutes, and {seconds} seconds", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'}),
                    html.Div(f"Total Walking Distance: {total_walking_distance_miles:.2f} miles", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'}),
                    html.Div(f"Total Out of Vehicle Time: {total_out_of_vehicle_time}", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'}),
                    html.Div(f"Total Walking Time: {total_walking_time}", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'})
                ]

            else:
                min_travel_time = travel_details['travel_time'].min()
                total_distance_meters = travel_details['distance'].sum()
                total_distance_miles = meters_to_miles(total_distance_meters)

                route_geometry = travel_details.loc[travel_details['travel_time'] == min_travel_time, 'geometry']
                if not route_geometry.empty:
                    route_coords = list(route_geometry.values[0].coords)
                    route_lons = [coord[0] for coord in route_coords]
                    route_lats = [coord[1] for coord in route_coords]

                    route_trace = go.Scattermapbox(
                        mode='lines',
                        lon=route_lons,
                        lat=route_lats,
                        line=dict(width=2, color='blue'),
                        name='Route'
                    )

                total_travel_time_seconds = min_travel_time.total_seconds()
                hours = int(total_travel_time_seconds // 3600)
                minutes = int((total_travel_time_seconds % 3600) // 60)
                seconds = int(total_travel_time_seconds % 60)

                output = [
                    html.Div(f"Calculated Travel Time: {hours} hours, {minutes} minutes, and {seconds} seconds", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'}),
                    html.Div(f"Total Distance: {total_distance_miles:.2f} miles", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'})
                ]

            if route_trace:
                current_figure.add_trace(route_trace)

            # Add origin and destination markers back if they were removed
            current_figure.add_trace(go.Scattermapbox(
                mode='markers+text',
                lon=[origin_lon, destination_lon],
                lat=[origin_lat, destination_lat],
                marker={'size': 10, 'color': ['red', '#93979C']},
                text=["Origin", "Destination"],
                textposition="bottom right",
                showlegend=False
            ))

            # Mapping of mode_of_travel to mode_styles keys
            mode_mapping = {
                'TRANSIT': 'mode-transit',
                'CAR': 'mode-car',
                'BICYCLE': 'mode-bike',
                'SHARED_RIDE': 'mode-shared-ride',
                'WALK': 'mode-walk'
            }

            # Update styles for selected mode button
            selected_mode_key = mode_mapping.get(mode_of_travel)
            if selected_mode_key:
                mode_styles[selected_mode_key]['background-color'] = '#74bf0c'
                mode_styles[selected_mode_key]['color'] = 'black'

            return origin, destination, current_figure, output, mode_styles['mode-transit'], mode_styles['mode-car'], mode_styles['mode-bike'], mode_styles['mode-shared-ride'], mode_styles['mode-walk']

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return origin, destination, current_figure, html.Div(f"Error calculating travel time: {str(e)}", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'}), mode_styles['mode-transit'], mode_styles['mode-car'], mode_styles['mode-bike'], mode_styles['mode-shared-ride'], mode_styles['mode-walk']

    return origin, destination, current_figure, html.Div("Enter valid coordinates and click 'Calculate Travel Time'.", style={'padding': '10px', 'background-color': '#74bf0c', 'color': 'black', 'margin-bottom': '10px'}), mode_styles['mode-transit'], mode_styles['mode-car'], mode_styles['mode-bike'], mode_styles['mode-shared-ride'], mode_styles['mode-walk']

@app.callback(
    Output('departure-time-div', 'style'),
    [Input('departure-time-radio', 'value')]
)
def toggle_departure_time_div(radio_value):
    if radio_value == 'future':
        return {'display': 'block'}
    return {'display': 'none'}

if __name__ == '__main__':
    app.run_server(debug=True)
