# Import necessary packages
import pandas as pd
import geopandas as gpd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

# Read data into the application
data = pd.read_csv('../data/clean/clean_meteorite_landings.csv')
data = gpd.GeoDataFrame(data, crs='EPSG:4326', geometry=gpd.points_from_xy(data['reclong'], data['reclat']))
world_data = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world_data = world_data.to_crs('EPSG:4326')

meteor_world_data = gpd.sjoin(world_data, data, how='inner', predicate='contains')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

server = app.server

app.layout = dbc.Container(
    html.Div(
        [
            # This Row contains the Headings
            dbc.Row(
                dbc.Col(
                    html.Div(
                        [
                            html.H1('Meteorite Exploration Dashboard'),
                            html.Hr(),
                            html.P('This is an exploratory tool for meteorite craters location data')
                        ]
                    ),
                    width='auto'
                )
            ),

            # This row contains the rest of the dashboard
            dbc.Row(
                [   
                    # Input column
                    dbc.Col(
                        html.Div(
                            [
                                html.H3('Filter Tools'),
                                dbc.Card(
                                    [
                                        html.H4('Year Range', style={'padding': 10}),
                                        dcc.RangeSlider(
                                            id="yearrange",
                                            min=data['year'].min(),
                                            max=data['year'].max(),
                                            step=1,
                                            value=[data['year'].min(), data['year'].max()],
                                            marks={
                                                860: {'label': '860'},
                                                1000: {'label': '1000'},
                                                1250: {'label': '1250'},
                                                1500: {'label': '1500'},
                                                1750: {'label': '1750'},
                                                1900: {'label': '1900'},
                                                2013: {'label': '2013'}
                                            },
                                            tooltip={"placement": "bottom", "always_visible": False}
                                        )
                                    ]
                                ),
                                html.Hr(),
                                dbc.Card(
                                    [
                                        html.H4('Type of Meteor', id='meteortype'),
                                        dbc.RadioItems(
                                            id='falltype',
                                            options=['Fell', 'Found', 'Both'],
                                            value='Both',
                                            labelStyle={'display': 'block'}
                                        )
                                    ],
                                    style={'padding': 10}
                                ),
                                html.Hr(),
                                dbc.Card(
                                    dbc.Switch(
                                        id='togglesize',
                                        label='Toggle meteor masses',
                                        value=True
                                    ),
                                    style={'padding': 10}
                                ),
                                html.Hr(),
                                dbc.Card(
                                    [
                                        html.H4('Mass of Meteorite'),
                                        dbc.RadioItems(
                                            id='massrange',
                                            options=[
                                                {'label': 'less than 10kg', 'value': 10},
                                                {'label': 'between 10kg and 100kg', 'value': 100},
                                                {'label': 'between 100kg and 1000kg', 'value': 1000},
                                                {'label': 'between 1000kg and 100000kg', 'value': 100000},
                                                {'label': 'greater than 100000kg', 'value': 100000000},
                                                {'label': 'all', 'value': 0}
                                            ],
                                            value=0,
                                            labelStyle={'display': 'block'}
                                        )
                                    ],
                                    style={'padding': 10}   
                                )
                            ]
                        ),
                        width=3,
                        style={'padding': 20}
                    ),

                    # Visualization column
                    dbc.Col(
                        [
                            # Row containing map
                            dbc.Row(
                                dbc.Col(
                                    html.Div(
                                        dcc.Graph(id='map_plot', figure={})
                                    )
                                ),
                            ),

                            # Row containing charts
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.Div(
                                            dbc.Card(
                                                dcc.Graph(id='histogram', figure={}),
                                                style={'padding': 10}
                                            )
                                        )
                                    ),
                                    dbc.Col(
                                        html.Div(
                                            dbc.Card(
                                                dcc.Graph(id='line', figure={}),
                                                style={'padding': 10}
                                            )
                                        )
                                    )
                                ],
                                style={'padding': 10}
                            )
                        ],
                        width=9
                    )
                ]
            )
        ]
    ),
    fluid=True
)
@app.callback(
    Output('map_plot', 'figure'),
    Input('yearrange', 'value'),
    Input('falltype', 'value'),
    Input('massrange', 'value'),
    Input('togglesize', 'value')
)
def update_map_plot(yearrange, ftype, rmass, toggle):
    
    if rmass == 10:
        massl, massh, size_max = 0, 10, 20
    elif rmass == 100:
        massl, massh, size_max = 10, 100, 20
    elif rmass == 1000:
        massl, massh, size_max = 100, 1000, 20
    elif rmass == 100000:
        massl, massh, size_max = 1000, 100000, 20
    elif rmass == 100000000:
        massl, massh, size_max = 100000, 100000000, 75
    else:
        massl, massh, size_max = 0, 100000000, 75

    yearl, yearh = yearrange[0], yearrange[1]
    filtered_data = meteor_world_data.query("year <= @yearh and year >= @yearl")
    filtered_data = filtered_data.query("mass >= @massl and mass <= @massh")
    if ftype == 'Fell':
        filtered_data = filtered_data.query("fall == 'Fell'")
    elif ftype == 'Found':
        filtered_data = filtered_data.query("fall == 'Found'")
    else:
        pass
    if toggle:
        fig = px.scatter_mapbox(filtered_data,
                                lat='reclat',
                                lon='reclong',
                                size='mass',
                                size_max=size_max,
                                color='mass',
                                mapbox_style='carto-darkmatter',
                                center={'lat': 0, 'lon': 0},
                                hover_name='name_left',
                                hover_data=['id', 'mass', 'name_right', 'year', 'recclass'],
                                zoom=1.5,
                                template='plotly_dark',
                                color_continuous_scale=px.colors.sequential.Sunsetdark)
        fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                          height=500)
    else:
        fig = px.scatter_mapbox(filtered_data,
                                lat='reclat',
                                lon='reclong',
                                color='mass',
                                mapbox_style='carto-darkmatter',
                                center={'lat': 0, 'lon': 0},
                                hover_name='name_left',
                                hover_data=['id', 'mass', 'name_right', 'year', 'recclass'],
                                zoom=1.5,
                                template='plotly_dark',
                                color_continuous_scale=px.colors.sequential.Sunsetdark)
        fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                          height=500)
    return fig

# callback for updating histogram plot
@app.callback(
    Output('histogram', 'figure'),
    Input('yearrange', 'value'),
    Input('falltype', 'value'),
    Input('massrange', 'value')
)
def update_histogram(yearrange, ftype, rmass):

    if rmass == 10:
        massl, massh = 0, 10
    elif rmass == 100:
        massl, massh = 10, 100
    elif rmass == 1000:
        massl, massh = 100, 1000
    elif rmass == 100000:
        massl, massh = 1000, 100000
    elif rmass == 100000000:
        massl, massh = 100000, 100000000
    else:
        massl, massh, size_max = 0, 100000000, 75

    yearl, yearh = yearrange[0], yearrange[1]
    filtered_data = meteor_world_data.query("year <= @yearh and year >= @yearl")
    filtered_data = filtered_data.query("mass >= @massl and mass <= @massh")
    if ftype == 'Fell':
        filtered_data = filtered_data.query("fall == 'Fell'")
    elif ftype == 'Found':
        filtered_data = filtered_data.query("fall == 'Found'")
    else:
        pass

    fig = px.bar((filtered_data
                  .groupby('continent')
                  .count()
                  .loc[:, ['pop_est']]
                  .rename(columns={'pop_est': 'count'})
                  .reset_index()
                  .sort_values('count', ascending=False)),
                 x='continent',
                 y='count',
                 labels={'count': 'Number of Meteorites', 'continent': 'Continent'},
                 template='plotly_dark')
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)',
                      height=300)
    return fig

# callback for updating line plot
@app.callback(
    Output('line', 'figure'),
    Input('yearrange', 'value'),
    Input('falltype', 'value'),
    Input('massrange', 'value')
)
def update_line(yearrange, ftype, rmass):

    if rmass == 10:
        massl, massh = 0, 10
    elif rmass == 100:
        massl, massh = 10, 100
    elif rmass == 1000:
        massl, massh = 100, 1000
    elif rmass == 100000:
        massl, massh = 1000, 100000
    elif rmass == 100000000:
        massl, massh = 100000, 100000000
    else:
        massl, massh, size_max = 0, 100000000, 75

    yearl, yearh = yearrange[0], yearrange[1]
    filtered_data = meteor_world_data.query("year <= @yearh and year >= @yearl")
    filtered_data = filtered_data.query("mass <= @massh and mass >= @massl")
    if ftype == 'Fell':
        filtered_data = filtered_data.query("fall == 'Fell'")
    elif ftype == 'Found':
        filtered_data = filtered_data.query("fall == 'Found'")
    else:
        pass

    fig = px.line((filtered_data
                   .groupby(['continent', 'year'])
                   .count()
                   .loc[:, ['pop_est']]
                   .rename(columns={'pop_est': 'count'})
                   .reset_index()),
                  x='year',
                  y='count',
                  color='continent',
                  labels={'count': 'Number of Meteorites', 'year': 'Year'},
                  template='plotly_dark')
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                      plot_bgcolor='rgba(0,0,0,0)',
                      paper_bgcolor='rgba(0,0,0,0)',
                      height=300)
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
