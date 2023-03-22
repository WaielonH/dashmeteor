# Import necessary packages
import pandas as pd
import geopandas as gpd
import plotly.express as px
import osmnx as ox
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

# Read data into the application
data = pd.read_csv('data/clean/clean_meteorite_landings.csv')
data = gpd.GeoDataFrame(data, crs='EPSG:4326', geometry=gpd.points_from_xy(data['reclong'], data['reclat']))
world_data = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
world_data = world_data.to_crs('EPSG:4326')

meteor_world_data = gpd.sjoin(world_data, data, how='inner', predicate='contains')
# Create default map
def create_map(data):
    fig = px.scatter_mapbox(data,
                            lat='reclat',
                            lon='reclong',
                            size='mass',
                            size_max=75,
                            color='mass',
                            mapbox_style='carto-darkmatter',
                            center={'lat': 0, 'lon': 0},
                            zoom=1,
                            template='plotly_dark',
                            color_continuous_scale=px.colors.sequential.Sunsetdark)
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    return fig
# Create default charts
histogram_plot = px.bar((meteor_world_data
                         .groupby('continent')
                         .count()
                         .loc[:, ['pop_est']]
                         .rename(columns={'pop_est': 'count'})
                         .reset_index()
                         .sort_values('count', ascending=False)),
                        x='continent',
                        y='count',
                        template='plotly_dark')
histogram_plot.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                             plot_bgcolor='rgba(0,0,0,0)',
                             paper_bgcolor='rgba(0,0,0,0)')

line_plot = px.line((meteor_world_data
                     .groupby(['continent', 'year'])
                     .count()
                     .loc[:, ['pop_est']]
                     .rename(columns={'pop_est': 'count'})
                     .reset_index()),
                    x='year',
                    y='count',
                    color='continent',
                    template='plotly_dark')
line_plot.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = html.Div(
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
                            html.Hr(),
                            html.H4('Year range:'),
                            dcc.DatePickerRange(
                                id='yearrange',
                                display_format='YYYY',
                                start_date='0860',
                                end_date='2013'),
                            html.Hr(),
                            html.H4('Type of Meteor'),
                            dcc.RadioItems(
                                id='falltype',
                                options=['Fell', 'Found', 'Both'],
                                value='Both',
                                labelStyle={'display': 'block'}
                            )
                        ]
                    ),
                    width=2
                ),

                # Visualization column
                dbc.Col(
                    [
                        # Row containing map
                        dbc.Row(
                            dbc.Col(
                                html.Div(
                                    dcc.Graph(id='map_plot', figure={})
                                ),
                                width=10
                            )
                        ),

                        # Row containing charts
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Div(
                                        dcc.Graph(id='histogram', figure=histogram_plot)
                                    )
                                ),
                                dbc.Col(
                                    html.Div(
                                        dcc.Graph(id='line', figure=line_plot)
                                    )
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

@app.callback(
    Output(component_id='map_plot', component_property='figure'),
    Input(component_id='yearrange', component_property='value')
)
def update_map_plot(yearfilter):
    filtered_data = data.query('year >= @yearfilter[0] & year <= @yearfilter[1]')
    fig = px.scatter_mapbox(filtered_data,
                            lat='reclat',
                            lon='reclong',
                            size='mass',
                            size_max=75,
                            color='mass',
                            mapbox_style='carto-darkmatter',
                            center={'lat': 0, 'lon': 0},
                            zoom=1,
                            template='plotly_dark',
                            color_continuous_scale=px.colors.sequential.Sunsetdark)
    fig.update_layout(margin={'r': 0, 't': 0, 'l': 0, 'b': 0})
    return fig
if __name__ == '__main__':
    app.run_server(debug=True)