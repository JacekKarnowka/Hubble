from typing import Type
import plotly.graph_objects as go
import pandas as pd
import dash
from dash import dcc, html, Output, Input, State
import requests
import json
import math

import Styles

pd.options.mode.chained_assignment = None

LOCALS_AVERAGE_PRICE = 10

# Define styles variables based on Styles.py

GRAPH_LINES_COLOR = Styles.GRAPH_LINES_COLOR

PLOT_BGCOLOR = Styles.PLOT_BGCOLOR

LEFT_MENU_COLOR = Styles.LEFT_MENU_COLOR

TEXT_STYLE_LEFT = Styles.TEXT_STYLE_LEFT

TEXT_STYLE_RIGHT = Styles.TEXT_STYLE_RIGHT

RIGHT_MENU_COLOR = Styles.RIGHT_MENU_COLOR

TEXT_STYLE = Styles.TEXT_STYLE

GRAPH_DIV_STYLE = Styles.GRAPH_DIV_STYLE

Graph_Height = Styles.Graph_Height

Graph_Width = Styles.Graph_Width

SLIDER_WIDTH = Styles.SLIDER_WIDTH


def get_coordinates(adress):
    
    if adress == '':
        raise TypeError("Empty string!")

    payload = {"query": [adress], "country": "GB"}

    answer = requests.get(
        "http://api.positionstack.com/v1/forward?access_key=5f5a76367052b2f26966faf4cd307507",
        params=payload,
    )
    if answer.status_code == 401:
        raise TypeError("Unauthorized")

    elif answer.status_code == 400:
        raise TypeError("Bad Request")

    elif answer.status_code != 200:
        raise TypeError("Wrong value")
        return "Wrong value, try again!"

    parse_answer = json.loads(answer.text)

    latitude = parse_answer["data"][0]["latitude"]
    longitude = parse_answer["data"][0]["longitude"]

    coordinates = [latitude, longitude]

    return coordinates


def generate_net(left_top, left_bottom, right_bottom, right_top):
    if len(left_top) != 2 or len(left_bottom) != 2 or len(right_bottom) != 2 or len(right_top) != 2:
        raise TypeError("Not proper length of corners coordinations")

    for corner in [left_top, left_bottom, right_bottom, right_bottom]:
        for i in range(0, len(corner)):
            if not isinstance(corner[i][0], int) and not isinstance(corner[i][0], float):
                raise TypeError("Wrong coordinates (not a number)")

    const_value = 10
    Lat = (left_top[0][0] - left_bottom[0][0]) / const_value
    Long = (left_top[1][0] - right_top[1][0]) / const_value

    net_latitude = []
    net_longitude = []

    for j in range(0, const_value):
        for i in range(0, const_value):
            net_latitude.append(
                [
                    left_top[0][0] - j * Lat,
                    left_top[0][0] - (j + 1) * Lat,
                    left_top[0][0] - (j + 1) * Lat,
                    left_top[0][0] - j * Lat,
                ]
            )

            net_longitude.append(
                [
                    left_top[1][0] - i * Long,
                    left_top[1][0] - i * Long,
                    left_top[1][0] - (i + 1) * Long,
                    left_top[1][0] - (i + 1) * Long,
                ]
            )

    created_net = [net_latitude, net_longitude]

    return created_net


def check_points(net, df):
    df_net = pd.DataFrame(
        columns=[
            "left_top_lat",
            "left_top_long",
            "left_bottom_lat",
            "left_bottom_long",
            "right_bottom_lat",
            "right_bottom_long",
            "right_top_lat",
            "right_top_long",
        ]
    )

    right_top_lat, right_bottom_lat = [], []
    left_bottom_lat, left_top_lat = [], []

    right_top_long, right_bottom_long = [], []
    left_bottom_long, left_top_long = [], []

    for i in range(0, len(net[0])):
        left_top_lat.append(net[0][i][0])
        left_top_long.append(net[1][i][0])

        left_bottom_lat.append(net[0][i][1])
        left_bottom_long.append(net[1][i][1])

        right_bottom_lat.append(net[0][i][2])
        right_bottom_long.append(net[1][i][2])

        right_top_lat.append(net[0][i][3])
        right_top_long.append(net[1][i][3])

    df_net["left_top_lat"] = left_top_lat
    df_net["left_top_long"] = left_top_long

    df_net["left_bottom_lat"] = left_bottom_lat
    df_net["left_bottom_long"] = left_bottom_long

    df_net["right_bottom_lat"] = right_bottom_lat
    df_net["right_bottom_long"] = right_bottom_long

    df_net["right_top_lat"] = right_top_lat
    df_net["right_top_long"] = right_top_long

    list_how_many_buildings = []
    list_average = []
    list_how_many_locals = []

    for k in range(0, len(df_net["left_bottom_lat"])):
        list_how_many_buildings.append(
            len(
                df.loc[
                    (df["Latitude"] > df_net.iloc[k]["left_bottom_lat"])
                    & (df["Longitude"] > df_net.iloc[k]["left_bottom_long"])
                    & (df["Latitude"] < df_net.iloc[k]["left_top_lat"])
                    & (df["Longitude"] < df_net.iloc[k]["right_bottom_long"])
                ]
            )
        )

        list_average.append(
            (
                sum(
                    df.loc[
                        (df["Latitude"] > df_net.iloc[k]["left_bottom_lat"])
                        & (df["Longitude"] > df_net.iloc[k]["left_bottom_long"])
                        & (df["Latitude"] < df_net.iloc[k]["left_top_lat"])
                        & (df["Longitude"] < df_net.iloc[k]["right_bottom_long"]),
                        "Price per person all options",
                    ]
                )
            )
        )

        list_how_many_locals.append(
            (
                sum(
                    df.loc[
                        (df["Latitude"] > df_net.iloc[k]["left_bottom_lat"])
                        & (df["Longitude"] > df_net.iloc[k]["left_bottom_long"])
                        & (df["Latitude"] < df_net.iloc[k]["left_top_lat"])
                        & (df["Longitude"] < df_net.iloc[k]["right_bottom_long"]),
                        "Option counter",
                    ]
                )
            )
        )

    df_net["How many buildings"] = list_how_many_buildings

    df_net["How many locals"] = list_how_many_locals

    df_net["Average price per person"] = list_average
    df_net["Average price per person"] = df_net.apply(
        lambda row: row["Average price per person"] / row["How many buildings"]
        if row["How many buildings"] != 0
        else 0,
        axis=1,
    )

    df_net.to_excel("./Data_xlsx/Net_data.xlsx", engine="xlsxwriter")

    return df_net


def figure_1(
    center_lat=51.509865,
    center_long=-0.118092,
    zoom_lvl=9,
    max_price=100000,
    min_price=0,
):
    df_new_point = pd.DataFrame()
    df_new_point[
        ["Title", "Latitude", "Longitude", "Price per person all options"]
    ] = df2[["Title", "Latitude", "Longitude", "Price per person all options"]]

    df_new_point[["new_point_Latitude", "new_point_Longitude"]] = [
        center_lat,
        center_long,
    ]

    df_new_point["distance_between"] = df_new_point.apply(
        lambda row: math.dist(
            [row["Latitude"], row["Longitude"]],
            [row["new_point_Latitude"], row["new_point_Longitude"]],
        ),
        axis=1,
    )

    fig1 = go.Figure()

    if center_lat != 51.509865 and center_long != -0.118092:
        df_tmp = df_new_point.sort_values("distance_between", ascending=True).head(
            LOCALS_AVERAGE_PRICE
        )
        estimated_local_value = round(
            float(sum(df_tmp["Price per person all options"])) / LOCALS_AVERAGE_PRICE, 2
        )

        latitude_list, longitude_list = [], []

        for i in range(0, 10):
            latitude_list.append(float(df_tmp.iloc[i]["Latitude"]))
            latitude_list.append(center_lat)

            longitude_list.append(float(df_tmp.iloc[i]["Longitude"]))
            longitude_list.append(center_long)

        fig1.add_trace(
            go.Scattermapbox(
                lat=latitude_list,
                lon=longitude_list,
                mode="lines",
                line=go.scattermapbox.Line(color="black", width=1.5),
            )
        )

        fig1.add_trace(
            go.Scattermapbox(
                name="<b>Picked <br>location</b>",
                lat=[center_lat],
                lon=[center_long],
                hovertemplate="<b> Estimated local value per person: {} pound for month</b><br>"
                "<b> Latitude:</b> {} <br>"
                "<b> Longitude</b> {} <br>".format(
                    estimated_local_value, center_lat, center_long
                ),
                mode="markers",
                marker=go.scattermapbox.Marker(
                    size=17,
                    opacity=1,
                    color="rgb(0, 0, 255)",
                ),
            )
        )

    df2["hoverText"] = "text"
    df2["hoverText"] = df2.apply(
        lambda row: "<b> Name: {} </b> <br>"
        "<b> Price per person: {} pounds</b> <br>"
        "<b> Latitude:</b> {} <br>"
        "<b> Longitude:</b> {} <br>".format(
            row["Title"],
            round(float(row["Price per person all options"]), 2),
            row["Latitude"],
            row["Longitude"],
        ),
        axis=1,
    )

    df2_range = df2[
        (df2["Price per person all options"] < max_price)
        & (df2["Price per person all options"] > min_price)
    ]

    fig1.add_trace(
        go.Scattermapbox(
            below="",
            name="<b>Default <br>locals</b>",
            lat=df2_range["Latitude"],
            lon=df2_range["Longitude"],
            hovertemplate=df2_range["hoverText"],
            mode="markers",
            marker=go.scattermapbox.Marker(
                colorbar={
                    "title": {
                        "text": "Average price<br>per person<br>[pounds]",
                        "font": {"size": 15, "family": "sans-serif"},
                    },
                    "x": 1,
                    "len": 1,
                    "thickness": 12,
                },
                showscale=True,
                colorscale="ylorrd_r",
                size=df2_range["Size"],
                opacity=0.9,
                color=df2_range["Price per person all options"],
            ),
        )
    )
    fig1.update_layout(
        showlegend=False,
        hovermode="closest",
        title={
            "text": "Price per person by location (building)",
            "font": {"size": 20, "color": "black", "family": "sans-serif"},
            "x": 0.5,
        },
        font={"color": "black", "size": 15},
        # width=Graph_Width,
        height=Graph_Height,
        geo=dict(bgcolor="black", projection_type="equirectangular"),
        paper_bgcolor=RIGHT_MENU_COLOR,
        plot_bgcolor=RIGHT_MENU_COLOR,
        coloraxis={"colorbar": {"xanchor": "left"}},
        mapbox=dict(
            style="dark",
            accesstoken=mapbox_access_token,
            bearing=10,
            center=go.layout.mapbox.Center(
                lat=center_lat,
                lon=center_long,
            ),
            pitch=0,
            zoom=zoom_lvl,
        ),
    )
    return fig1


def figure_2():
    fig2 = go.Figure()

    for i in range(0, len(net[0])):
        if df_points["How many locals"][i] != 0:
            fig2.add_trace(
                go.Scattermapbox(
                    name="{} locals".format(df_points["How many locals"][i]),
                    lat=net[0][i],
                    lon=net[1][i],
                    mode="lines",
                    fill="toself",
                    fillcolor="rgba({},0,0,{})".format(
                        int(df_points["How many locals"][i] / 2 + 21),
                        0.15 if df_points["How many locals"][i] < 3 else 0.55,
                    ),
                    line=go.scattermapbox.Line(color="black", width=0),
                )
            )

    fig2.update_layout(
        showlegend=True,
        hovermode="closest",
        title={
            "text": "Density map- how many locals to rent",
            "font": {"size": 20, "color": "black"},
            "x": 0.5,
        },
        font={"color": "black", "size": 12},
        # width=Graph_Width,
        height=Graph_Height,
        geo=dict(bgcolor="black"),
        paper_bgcolor=RIGHT_MENU_COLOR,
        plot_bgcolor=RIGHT_MENU_COLOR,
        mapbox=dict(
            style="dark",
            accesstoken=mapbox_access_token,
            bearing=10,
            center=go.layout.mapbox.Center(
                lat=51.516865,
                lon=-0.118092,
            ),
            pitch=0,
            zoom=11,
        ),
    )
    return fig2


def figure_3():
    fig3 = go.Figure()

    for i in range(0, len(net[0])):
        if df_points["Average price per person"][i] != 0:
            fig3.add_trace(
                go.Scattermapbox(
                    name="Price {}".format(
                        round(df_points["Average price per person"][i], 2)
                        if df_points["Average price per person"][i] != 0
                        else "No data"
                    ),
                    lat=net[0][i],
                    lon=net[1][i],
                    mode="lines",
                    fill="toself",
                    fillcolor="rgba({},0,0,{})".format(
                        int(df_points["Average price per person"][i] / 3.5 - 20),
                        0.15 if df_points["How many buildings"][i] < 3 else 0.55,
                    ),
                    line=go.scattermapbox.Line(color="black", width=0),
                )
            )

    fig3.update_layout(
        showlegend=True,
        hovermode="closest",
        title={
            "text": "Average price per person",
            "font": {"size": 20, "color": "black", "family": "sans-serif"},
            "x": 0.5,
        },
        font={"color": "black", "size": 12},
        # width=Graph_Width,
        height=Graph_Height,
        geo=dict(bgcolor="black"),
        paper_bgcolor=RIGHT_MENU_COLOR,
        plot_bgcolor=RIGHT_MENU_COLOR,
        mapbox=dict(
            style="dark",
            accesstoken=mapbox_access_token,
            bearing=10,
            center=go.layout.mapbox.Center(
                lat=51.516865,
                lon=-0.118092,
            ),
            pitch=0,
            zoom=11,
        ),
    )
    return fig3


def get_distance(x1, y1, x2, y2):
    for number in [x1, y1, x2, y2]:
        if not isinstance(number, int) and not isinstance(number, float):
            raise TypeError("Coordinates not a number!")
    earthRadius = 6371
    dist = (
        math.acos(
            math.sin(x2 * math.pi / 180.0) * math.sin(x1 * math.pi / 180.0)
            + math.cos(x2 * math.pi / 180.0)
            * math.cos(x1 * math.pi / 180.0)
            * math.cos((y1 - y2) * math.pi / 180.0)
        )
        * earthRadius
    )
    return round(dist, 5)


def figure_4(min_people=0, max_people=300, names_list=None):
    fig4 = go.Figure()

    df_fig_4 = df.sort_values("Up to [people]", ascending=True)
    df_fig_4["distance_from_center"] = 0
    df_fig_4["distance_from_center"] = df_fig_4.apply(
        lambda row: get_distance(
            51.516865, -0.118092, float(row["Latitude"]), float(row["Longitude"])
        ),
        axis=1,
    )

    df_fig_4_range = df_fig_4[
        (df_fig_4["Up to [people]"] < max_people)
        & (df_fig_4["Up to [people]"] > min_people)
    ]

    df_fig_4_range["color"] = df_fig_4_range["distance_from_center"].apply(
        lambda x: "rgb({},0,0)".format(255 - int(x * 585))
    )

    if names_list is not None:
        list(set(names_list))
        df_fig_4_range = df_fig_4_range[df_fig_4_range["Title"].isin(names_list)]
        print(names_list)

    fig4.add_trace(
        go.Scatter(
            x=df_fig_4_range["Up to [people]"],
            y=df_fig_4_range["Office price"],
            text=df_fig_4_range["Title"],
            mode="markers",
            marker={
                "color": df_fig_4_range["distance_from_center"],
                "size": 6,
                "opacity": 0.8,
                "showscale": True,
                "colorscale": "ylorrd_r",
                "colorbar": {
                    "title": {
                        "text": "Distance<br>[km]",
                        "font": {"size": 15, "family": "sans-serif"},
                    },
                    "x": 1,
                    "len": 1,
                    "thickness": 12,
                },
                "line": {"width": 0.5, "color": "black"},
            },
        )
    )

    fig4.update_layout(
        hovermode="closest",
        title={
            "text": "Price max people and distance from centrum",
            "font": {"size": 20, "color": "black"},
            "x": 0.5,
        },
        font={"color": "black", "size": 15},
        # width=Graph_Width,
        showlegend=False,
        height=Graph_Height,
        paper_bgcolor=RIGHT_MENU_COLOR,
        plot_bgcolor=RIGHT_MENU_COLOR,
    )

    fig4.update_yaxes(
        title_text="Office price",
        gridcolor=GRAPH_LINES_COLOR,
        linecolor=GRAPH_LINES_COLOR,
        gridwidth=0.3,
        linewidth=0.3,
        zerolinecolor=GRAPH_LINES_COLOR,
    ),

    fig4.update_xaxes(
        title_text="Max number of people",
        gridcolor=GRAPH_LINES_COLOR,
        linecolor=GRAPH_LINES_COLOR,
        gridwidth=0.3,
        linewidth=0.3,
        zerolinecolor=GRAPH_LINES_COLOR,
    )

    fig4.update_annotations(
        font={"size": 20, "family": "sans-serif", "color": "#efb636"}
    )

    return fig4


pd.set_option("display.max_rows", 50, "display.max_columns", 20)
df = pd.read_excel("./Data_xlsx/Cleaned_data.xlsx")

mapbox_access_token = open("./map_box_token").read()

df_average_prize = df.drop_duplicates(subset=["Title"])

df2 = df.drop_duplicates(subset=["Title"])

df2["Option counter"] = df2["Title"].apply(lambda x: len(df.loc[df["Title"] == x]))

df2["Option sum price"] = df2["Title"].apply(
    lambda x: sum(df.loc[df["Title"] == x, "Office price"])
)

df2["Option people sum"] = df2["Title"].apply(
    lambda x: sum(df.loc[df["Title"] == x, "Up to [people]"])
)

df2["Price per person all options"] = df2.apply(
    lambda row: row["Option sum price"] / row["Option people sum"]
    if row["Up to [people]"] != "NUN"
    else row["Option sum price"],
    axis=1,
)

df2["Price per person all options"] = df2["Price per person all options"].apply(
    lambda x: 1500 if x > 1500 else x
)

df2["Price per person"] = df2.apply(
    lambda row: row["Office price"] / row["Up to [people]"]
    if row["Up to [people]"] != "NUN"
    else row["Office price"],
    axis=1,
)

df2.loc[:, "Size"] = 12

corners = []

left_top_corner = [[51.5574], [-0.18851]]

left_bottom_corner = [[51.4836375], [-0.18851]]

right_bottom_corner = [[51.4836375], [-0.04555399]]

right_top_corner = [[51.5574], [-0.04555399]]

net = generate_net(
    left_top_corner, left_bottom_corner, right_bottom_corner, right_top_corner
)

df_points = check_points(net, df2)

max_office_price = df2["Price per person all options"].max()
min_office_price = df2["Price per person all options"].min()

max_office_full = 300
min_office_full = df["Up to [people]"].min()

app = dash.Dash()
server = app.server
app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    children=[
                        html.H1(
                            children="Locals to rent in London \n",
                            style={"textAlign": "center", "color": "#efb636"},
                        )
                    ],
                    style={"padding-top": "2%"},
                ),
                html.H4(
                    """Enter address to check 
                its estimated value:""",
                    style={
                        "font-size": 20,
                        "font-family": "sans-serif",
                        "color": "white",
                        "verticalAlign": "top",
                        "marginTop": "10%",
                        "marginLeft": "5%",
                        "marginRight": "5%",
                    },
                ),
                dcc.Textarea(
                    id="input_address",
                    value="",
                    style={
                        "font-size": 20,
                        "font-family": "sans-serif",
                        "color": "white",
                        "verticalAlign": "top",
                        "marginTop": "5%",
                        "marginLeft": "5%",
                        "width": "90%",
                        "height": 200,
                        "background": PLOT_BGCOLOR,
                    },
                ),
                html.Button(
                    id="submit_button",
                    n_clicks=0,
                    children="Submit",
                    style={
                        "font-size": 20,
                        "marginTop": "5%",
                        "marginLeft": "5%",
                        "height": "50px",
                        "width": "100px",
                        "color": "white",
                        "border": "1px solid {}".format(GRAPH_LINES_COLOR),
                        "background": PLOT_BGCOLOR,
                    },
                ),
                html.H4(
                    id="estimated_value",
                    style={
                        "font-size": 20,
                        "font-family": "sans-serif",
                        "color": "white",
                        "verticalAlign": "top",
                        "marginTop": "10%",
                        "marginLeft": "5%",
                    },
                ),
                dcc.Store(id="estimated"),
            ],
            style={
                "display": "inline-block",
                "width": "20%",
                "height": "100%",
                "background-color": LEFT_MENU_COLOR,
            },
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="fig_1", figure=figure_1())],
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        dcc.RangeSlider(
                                            math.floor(min_office_price),
                                            max_office_price,
                                            value=[min_office_price, max_office_price],
                                            id="price_slider",
                                            tooltip={
                                                "placement": "bottom",
                                                "always_visible": True,
                                            },
                                        ),
                                    ],
                                    style={"width": "90%", "marginLeft": "5%"},
                                )
                            ]
                        ),
                    ],
                    style={"display": "inline-block", "width": "58%"},
                ),
                html.Div(
                    [
                        html.Div([dcc.Graph(id="fig_4", figure=figure_4())], style={}),
                        html.Div(
                            [
                                dcc.RangeSlider(
                                    math.floor(min_office_full),
                                    max_office_full,
                                    value=[min_office_full, max_office_full],
                                    id="price_full",
                                    tooltip={
                                        "placement": "bottom",
                                        "always_visible": True,
                                    },
                                )
                            ],
                            style={"width": "90%", "marginLeft": "5%"},
                        ),
                    ],
                    style={"display": "inline-block", "width": "38%"},
                ),
                html.Div(
                    [
                        html.Div(
                            [dcc.Graph(id="fig_2", figure=figure_2())],
                            style={"display": "inline-block", "width": "48%"},
                        ),
                        html.Div(
                            [dcc.Graph(id="fig_3", figure=figure_3())],
                            style={"display": "inline-block", "width": "48%"},
                        ),
                    ],
                    style={"marginTop": "5%"},
                ),
            ],
            style=GRAPH_DIV_STYLE,
        ),
    ],
    style={"height": "1500px", "background-color": RIGHT_MENU_COLOR},
)

df2.to_excel("./Data_xlsx/Data_Price_per_person.xlsx", engine="xlsxwriter")


# 34-37 Liverpool St, London


@app.callback(
    Output("fig_1", "figure"),
    [Input("submit_button", "n_clicks"), Input("price_slider", "value")],
    [State("input_address", "value")],
)
def update_output(n_clicks, value_slider, value):
    if get_coordinates(value) == "Wrong value, try again!":
        return figure_1(min_price=value_slider[0], max_price=value_slider[1])

    lat = float(str(get_coordinates(value)).split(",")[0][1:])
    long = float(str(get_coordinates(value)).split(",")[1][1:-1])

    if n_clicks > 0:
        if value == "home":
            return figure_1()

        return figure_1(
            lat, long, 16, min_price=value_slider[0], max_price=value_slider[1]
        )


@app.callback(
    Output("fig_4", "figure"),
    [Input("price_full", "value"), Input("fig_1", "selectedData")],
)
def update_fig_4(value, selectedData):
    if selectedData is not None:
        pts = selectedData["points"]
        print(pts)
        names = []

        for i in pts:
            names.append(i["hovertemplate"].split(":")[1].split("</b")[0][1:-1])

        return figure_4(value[0], value[1], names)

    return figure_4(value[0], value[1])


if __name__ == "__main__":
    app.run_server()
