import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import datetime
import pickle
# import cloudpickle as cp
# from urllib.request import urlopen
# import plotly.graph_objects as go
# import json

mapbox_access_token = 'pk.eyJ1IjoicG9rZXBsYXllcjQxMCIsImEiOiJjazExNTFjaXEwM2ZoM21wN3lmdnV0MDh3In0.knrnpp-HCI4InopZXhd1qg' # other one I found: # 'pk.eyJ1IjoiY2hyaWRkeXAiLCJhIjoiY2ozcGI1MTZ3MDBpcTJ3cXR4b3owdDQwaCJ9.8jpMunbKjdq1anXwU5gxIw'
mapbox_access_token_secret_doesnt_work = 'sk.eyJ1IjoicG9rZXBsYXllcjQxMCIsImEiOiJjazExNTZtZDAwZDVkM25zN3FqMWVnNGd4In0.aEnrYJXfBPqwo8G9rA0mNw'

path_data = 'http://sumitdutta.com/'

infile= open('trailbeings.db', 'rb') #cp.load(urlopen(path_data+'trailbeings.db'), 'rb')
df_trail_info_master = pickle.load(infile)
df_park_info_master = pickle.load(infile)
infile.close()

# print(df_trail_info)
# print(df_trail_info.columns)
# print(df_trail_info.dtypes)
# print(df_trail_info['animals'])

# df_trail_info_test = pd.read_csv('http://sumitdutta.com/'+'traillatlon.csv')
# print(df_trail_info_test.columns)
# print(df_trail_info_test.dtypes)

df_trail_info_master.rename(columns={'trail_lat': 'latitude', 'trail_lon': 'longitude'}, inplace=True)

park_list_options = [] # e.g., [{'label': 'Yellowstone National Park', 'value': 'yellowstone-national-park'}]
df_park_list = df_trail_info_master[['park','park_name']].drop_duplicates()
for park_index, park_row in df_park_list.iterrows():
    park_list_options.append({'label': park_row['park_name'], 'value': park_row['park']})

# Pick default park
df_trail_info = df_trail_info_master[df_trail_info_master['park'] == 'yellowstone-national-park']
park_name = str(df_trail_info[['park','park_name']].drop_duplicates().iloc[0]['park_name'])

# String limiter: # df_trail_info['animals'] = df_trail_info['animals'].str.slice(0,160)
# Manual override: # df_trail_info['animals'] = "<br>1. Rail: 50% <br>2. Crow: 60% <br>3. Bear: 80% <br>4. Bison/buffalo: 100%"

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, url_base_pathname='/ww/')
app.title = 'Wildlife Watch by Sumit Dutta'

server = app.server

app.layout = html.Div(children=[
    html.Div(children=[
        html.Div([
            html.Div([
                html.H1(children='Wildlife Watch'),
                html.Div(children='''
                    Know what wildlife you can expect at the National Parks.
                ''', style={'font-weight': 'bold'}),
            ], style={'display': 'inline-block', 'width': '64%', 'vertical-align': 'middle'}),
            html.Div([
                html.A([
                    html.Img(src='assets/elk.jpg', style={'width': '200px', 'height': '150px'}),
                ], href='https://drive.google.com/open?id=1jtZrWFCYyTAgIp9lYkK9GqF23ZeJ4LhGjoxoVO3ni5A'),
            ], style={'display': 'inline-block', 'width': '34%', 'text-align': 'right', 'vertical-align': 'middle'})
        ]),
        html.Div(children=[
            html.H5(children='Park:', style={'font-weight': 'bold'}),
            # options = [{'label': 'Yellowstone National Park', 'value': 'yellowstone-national-park'}]
            dcc.Dropdown(id='park', options=park_list_options)
        ]),

        # # Consider removing the below dropdown, since this data should just appear on the map
        # dcc.Dropdown(id='trail', options=[
        #     {'label': 'Upper Geyser Basin and Old Faithful Observation Point Loop', 'value': 'upper-geyser-basin-and-old-faithful-observation-point-loop'}
        # ]),

        html.Div(children=[
            html.H5(children='Season/month:', style={'font-weight': 'bold'}),
            dcc.Dropdown(id='month', options=[
                {'label': 'January', 'value': '01'},
                {'label': 'February', 'value': '02'},
                {'label': 'March', 'value': '03'},
                {'label': 'April', 'value': '04'},
                {'label': 'May', 'value': '05'},
                {'label': 'June', 'value': '06'},
                {'label': 'July', 'value': '07'},
                {'label': 'August', 'value': '08'},
                {'label': 'September', 'value': '09'},
                {'label': 'October', 'value': '10'},
                {'label': 'November', 'value': '11'},
                {'label': 'December', 'value': '12'}
            ])
        ]),

        html.Button('Find wildlife!', id='button'),

        html.Div(id='output'),
    ], style={'width': '49%', 'height': '95vh', 'display': 'inline-block', 'vertical-align': 'top', 'background-image': 'url("assets/yellowstone.jpg")', 'background-repeat': 'no-repeat', 'background-position': '0 0'}),
    html.Div(children=[
        html.Div(
            [dcc.Graph(
                id='main_graph',
                style={'width':'100%', 'display': 'inline-block'}
                # figure={
                #     'data': [{
                #         'lat': df_trail_info.trail_lat, 'lon': df_trail_info.trail_lon, 'type': 'scattermapbox'
                #     }],
                #     'layout': {
                #         'mapbox': {
                #             'accesstoken': (mapbox_access_token),
                #             'center': dict(lat=df_trail_info.trail_lat.mean(), lon=df_trail_info.trail_lon.mean()),
                #             'zoom': 9,
                #         },
                #         'title': "Park map",
                #         'margin': {
                #             'l': 30, 'r': 30, 'b': 20, 't': 40
                #         },
                #         'autosize': True,
                #         'automargin': True,
                #     }
                # }
            )],
        )
    ], style={'width': '49%', 'display': 'inline-block', 'vertical-align': 'top'})
], style={'columnCount': 1})

@app.callback(
    Output('output', 'children'),
    [Input('button', 'n_clicks')],
    state=[State('park', 'value'), State('month', 'value')]
)
def clicks(n_clicks, park, value):
    if (park is None or value is None):
        return ""
    df_park_info = df_park_info_master[(df_park_info_master['park'] == str(park)) & (df_park_info_master['month'] == int(value))]
    animal_text = str(df_park_info.iloc[0]['animals'])
    animal_listitems = [html.P(x) for x in animal_text.split('<br>')]
    return [html.P("Animals to expect in {}:".format(str(datetime.date(2000, int(value), 1).strftime('%B')))),
            html.Div(animal_listitems)]  # (park, value)

    # # Old static information function is below:
    # showtext = {}
    # showtext[''] = ""
    # showtext['01'] = ['Eurasian elk: common', 'Rocky Mountain elk: abundant', 'checkerspot: common', 'fritillary: common']
    # showtext['02'] = ['Eurasian elk: common', 'Rocky Mountain elk: abundant', 'checkerspot: common', 'fritillary: common']
    # showtext['03'] = ['Eurasian elk: common', 'Rocky Mountain elk: abundant', 'checkerspot: common', 'fritillary: common']
    # showtext['04'] = ['American black bear: common', 'Grizzly bear: common', 'bison: abundant', 'beaver: common']
    # showtext['05'] = ['American black bear: common', 'Grizzly bear: common', 'bison: abundant', 'beaver: common']
    # showtext['06'] = ['American black bear: common', 'Grizzly bear: common', 'bison: abundant', 'beaver: common']
    # showtext['07'] = ['American black bear: common', 'Grizzly bear: common', 'bison: abundant', 'beaver: common']
    # showtext['08'] = ['American black bear: common', 'Grizzly bear: common', 'bison: abundant', 'beaver: common']
    # showtext['09'] = ['American black bear: common', 'Grizzly bear: common', 'bison: abundant', 'beaver: common']
    # showtext['10'] = ['Eurasian elk: common', 'Rocky Mountain elk: abundant', 'checkerspot: common', 'fritillary: common']
    # showtext['11'] = ['Eurasian elk: common', 'Rocky Mountain elk: abundant', 'checkerspot: common', 'fritillary: common']
    # showtext['12'] = ['Eurasian elk: common', 'Rocky Mountain elk: abundant', 'checkerspot: common', 'fritillary: common']
    # return [html.P("Animals to expect in {}:".format(str(datetime.date(2000, int(value), 1).strftime('%B')))), html.Ol([html.Li(x) for x in showtext[value]])] # (park, value)

# Selectors -> main graph
@app.callback(
    Output("main_graph", "figure"),
    [Input('button', 'n_clicks')],
    state=[State('park', 'value'), State('month', 'value')]
)
def make_main_figure(n_clicks, park, value):
    if (park is None or value is None):
        park = 'yellowstone-national-park'
        value = 1
    df_trail_info = df_trail_info_master[df_trail_info_master['park'] == str(park)]
    park_name = str(df_trail_info[['park', 'park_name']].drop_duplicates().iloc[0]['park_name'])

    figure = px.scatter_mapbox(df_trail_info, lat="latitude", lon="longitude", hover_name="trail_name", hover_data=["animals"],
                               color_discrete_sequence=["green"], zoom=9) # height=300
    figure.update_layout(title='Park' if ((park is None) or (value is None)) else str(park_name)+' in '+str(datetime.date(2000, int(value), 1).strftime('%B')))
    figure.update_layout(mapbox_accesstoken=mapbox_access_token)
    figure.update_layout(margin={'l': 30, 'r': 30, 'b': 20, 't': 40})
    figure.update_layout(mapbox_style='outdoors')
    # figure.show()
    return figure
#
#     # dff = filter_dataframe(df, well_statuses, well_types, year_slider)
#     #
#     traces = []
#     trace = dict(
#         type="scattermapbox",
#         lon=pd.Series([-78.05]),
#         lat=pd.Series([42.54]),
#         text=pd.Series(['Testing']),
#         customdata=pd.Series(['Testing']),
#         name='Testing',
#         marker=dict(size=4, opacity=0.6),
#     )
#     traces.append(trace)
#
#     # if main_graph_layout is not None and "locked" in selector:
#     #     lon = float(main_graph_layout["mapbox"]["center"]["lon"])
#     #     lat = float(main_graph_layout["mapbox"]["center"]["lat"])
#     #     zoom = float(main_graph_layout["mapbox"]["zoom"])
#     #     layout["mapbox"]["center"]["lon"] = lon
#     #     layout["mapbox"]["center"]["lat"] = lat
#     #     layout["mapbox"]["zoom"] = zoom
#
#     figure = dict(data=traces, layout=layout)
#     return figure


if __name__ == '__main__':
    app.run_server(debug=True)
