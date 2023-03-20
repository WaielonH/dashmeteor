# Import necessary packages
import pandas as pd
import plotly.express as px
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

# Read data into the application
data = pd.read_csv('data/clean/clean_meteorite_landings.csv')

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
                            html.H2('This will be the input panel'),
                            html.Hr(),
                            html.P('Enter all inputs here')
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
                                    'The map goes here'
                                ),
                                width=6
                            )
                        ),

                        # Row containing charts
                        dbc.Row(
                            [
                                dbc.Col('Plot A'),
                                dbc.Col('Plot B')
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)