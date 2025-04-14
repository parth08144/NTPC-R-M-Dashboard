import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc


df = pd.read_csv("Repair_Maintenance_Budget_vs_Actual.csv")
df["Utilization %"] = (df["Actual"] / df["Budget"]) * 100
df["Status"] = df.apply(lambda row: "Over" if row["Actual"] > row["Budget"] else "Under", axis=1)
df["Variance %"] = ((df["Actual"] - df["Budget"]) / df["Budget"]) * 100


app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "NTPC R&M Pro Dashboard"


app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.Img(src="/assets/ntpc_logo.png", height="60px"), width="auto"),
        dbc.Col(html.H2("NTPC Repair & Maintenance Dashboard", className="text-center mb-0"), width=True),
    ], className="my-3 align-items-center"),

    dbc.Row([
        dbc.Col([
            html.Label("Select Status:"),
            dcc.Dropdown(
                id="status-filter",
                options=[{"label": s, "value": s} for s in df["Status"].unique()],
                value=df["Status"].unique().tolist(),
                multi=True,
                className="mb-2"
            ),
        ], md=4),

        dbc.Col([
            html.Label("Utilization Range:"),
            dcc.RangeSlider(
                id="util-slider",
                min=0, max=200, step=5,
                value=[0, 150],
                marks={i: f"{i}%" for i in range(0, 201, 25)}
            )
        ], md=6),

        dbc.Col([
            html.Label("Toggle View:"),
            dcc.Checklist(
                id="chart-toggle",
                options=[
                    {"label": " Bar", "value": "bar"},
                    {"label": " Pie", "value": "pie"}
                ],
                value=["bar", "pie"],
                inline=True,
                inputStyle={"margin-right": "5px", "margin-left": "10px"}
            )
        ], md=2),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="bar-chart"), md=6),
        dbc.Col(dcc.Graph(id="pie-chart"), md=6)
    ]),

    dbc.Row([
        dbc.Col([
            html.Button("⬇ Download Filtered Data", id="btn-download", className="btn btn-success"),
            dcc.Download(id="download-csv")
        ], className="text-end mb-3")
    ]),

    dbc.Row([
        dbc.Col([
            html.H5("Detailed Table"),
            dash_table.DataTable(
                id='data-table',
                columns=[{"name": i, "id": i} for i in df.columns],
                style_data_conditional=[
                    {"if": {"filter_query": "{Status} eq 'Over'"}, "backgroundColor": "#ffe6e6"},
                    {"if": {"filter_query": "{Status} eq 'Under'"}, "backgroundColor": "#e6f7ff"}
                ],
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "padding": "5px"},
                page_size=10
            )
        ])
    ])
], fluid=True)


# Callbacks
@app.callback(
    Output("bar-chart", "figure"),
    Output("pie-chart", "figure"),
    Output("data-table", "data"),
    Input("status-filter", "value"),
    Input("util-slider", "value"),
    Input("chart-toggle", "value")
)
def update_charts(status_values, util_range, chart_toggle):
    filtered_df = df[
        (df["Status"].isin(status_values)) &
        (df["Utilization %"] >= util_range[0]) &
        (df["Utilization %"] <= util_range[1])
    ]

    bar_fig = px.bar(
        filtered_df, x="Category", y=["Budget", "Actual"],
        barmode="group", title="Budget vs Actual by Category"
    )

    pie_fig = px.pie(
        filtered_df, names="Category", values="Actual",
        title="Actual Spend Distribution"
    )

    return (
        bar_fig if "bar" in chart_toggle else {},
        pie_fig if "pie" in chart_toggle else {},
        filtered_df.to_dict("records")
    )


@app.callback(
    Output("download-csv", "data"),
    Input("btn-download", "n_clicks"),
    State("status-filter", "value"),
    State("util-slider", "value"),
    prevent_initial_call=True
)
def download_filtered(n_clicks, status_values, util_range):
    filtered_df = df[
        (df["Status"].isin(status_values)) &
        (df["Utilization %"] >= util_range[0]) &
        (df["Utilization %"] <= util_range[1])
    ]
    return dcc.send_data_frame(filtered_df.to_csv, "NTPC_RM_filtered.csv")


# Run the server
if __name__ == "__main__":
    app.run(debug=True)

