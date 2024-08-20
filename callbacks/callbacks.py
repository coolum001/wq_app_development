from dash import dcc, html, Input, Output, State, ALL, ctx
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
import numpy as np
import os.path
import utils.constants as c
import utils.functions as f


def callbacks(app):
    @app.callback(
        [
            Output("map", "figure"),
            Output("map", "selectedData"),
            Output("container-site-info", "children"),
        ],
        [
            Input("map", "selectedData"),
            Input("dropdown-status", "value"),
            Input("dropdown-waterway", "value"),
        ],
        [State("map", "figure"), State("map", "clickData")],
        prevent_initial_call=True,
    )
    def update_map(selected_site, status, waterway, fig, clicked_site):
        """
        TODO
        """

        # Loading the sites dataframe.
        df_sites = f.get_df_sites()

        # Determination of the code of the selected site on the map.
        # Property 'selectedData' (i.e. selected_site) : data from latest select event. Can contain one or multiple points depending on whether the user did a Click or Shift+Click. Dictionary format: {'points': [dict_point1_info, dict_point2_info, ...]}
        # Property 'clickData' (i.e. clicked_site): data from latest click event. Contains only one point, the last one clicked. Dictionary format: { 'points': [dict_point_info]}
        if not selected_site:
            site_code = None  # Useful when a previously selected site is deselected.
        else:
            site_code = clicked_site["points"][0][
                "customdata"
            ]  # We do not want to allow the selection of multiple sites on the map but there is no option to disable multiple sites selection with Shift+Click at the moment, so we use the clickData property to determine which site has been selected.

        # Filtering sites according to status and waterway filters.
        if status != "all":
            df_sites = df_sites[df_sites["status"] == status]

        if waterway != "all":
            df_sites = df_sites[df_sites["waterway"] == waterway]

        # Deletion of the selected site if it is no longer included in the new filtered sites.
        if site_code not in df_sites["site_code"].values:
            site_code = None

        if site_code:
            # Modification of the 'selectedData' property of the map to ensure that only one point is selected, even if the user makes a multiple selection with Shift+Click.
            clicked_site["points"][0].pop("bbox")
            selectedData = clicked_site

            # Creation of the site information section.
            row_site = df_sites[df_sites["site_code"] == site_code].squeeze()
            site_info_content = [
                html.Div(f"{site_code} - {row_site['site_name']}", className="mb-2"),
                dbc.Table(
                    [
                        html.Tbody(
                            [
                                html.Tr([html.Td("Status"), html.Td("Coordinates")]),
                                html.Tr(
                                    [
                                        html.Td(row_site["status"]),
                                        html.Td(
                                            f"{row_site['latitude']}° / {row_site['longitude']}°"
                                        ),
                                    ]
                                ),
                                html.Tr([html.Td("Waterway"), html.Td("Waterbody")]),
                                html.Tr(
                                    [
                                        html.Td(row_site["waterway"]),
                                        html.Td(
                                            f"{row_site['waterbody_code']} - {row_site['waterbody_type']}"
                                        ),
                                    ]
                                ),
                            ],
                            className="fs-xs",
                        )
                    ],
                    className="mb-0 table-small-y-padding",
                    bordered=True,
                    striped=True,
                ),
            ]
        else:
            selectedData = None
            site_info_content = c.msg_no_site

        # Creation of a new map figure based on the selected site and the filtered sites.
        map_figure = f.get_map_figure(df_sites, site_code, fig["layout"])

        return map_figure, selectedData, site_info_content

    @app.callback(
        [
            Output("container-graph", "children"),
            Output("container-wtr-info", "children"),
            Output("mem-selected-wtr", "data"),
            Output("button-dl-site-sheet", "disabled"),
            Output("button-dl-raw-data", "disabled"),
        ],
        [
            Input("map", "selectedData"),
            Input({"type": "graph", "index": ALL}, "selectedData"),
            Input("dropdown-parameter", "value"),
            Input("switch-median", "value"),
            Input("switch-bands", "value"),
        ],
        [
            State({"type": "graph", "index": ALL}, "clickData"),
            State("mem-selected-wtr", "data"),
        ],
        prevent_initial_call=True,
    )
    def create_graph(
        selected_site,
        selected_wtr,
        parameter,
        switch_median,
        switch_bands,
        clicked_wtr,
        last_selected_wtr,
    ):
        """
        TODO
        """

        graph = c.msg_no_graph
        wtr_info_content = c.msg_no_point  # wtr = Water Testing Result
        wtr_id = None
        btn_dl_site_sheet_disabled, btn_dl_raw_data_disabled = True, True

        if selected_site:
            # Loading dataframes.
            df_sites = f.get_df_sites()
            df_water_testing_results = f.get_df_water_testing_results()

            btn_dl_site_sheet_disabled, btn_dl_raw_data_disabled = False, False

            # Retrieving the code and name of the site selected on the map.
            site_code = selected_site["points"][0]["customdata"]
            site_name = df_sites.loc[
                df_sites["site_code"] == site_code, "site_name"
            ].to_numpy()[0]

            # Retrieving water testing results for the selected site.
            df = df_water_testing_results[
                df_water_testing_results["site_code"] == site_code
            ]

            # Deletion of dataframe rows for which there are no values for the selected parameter.
            df = df.dropna(subset=parameter)

            if len(df[parameter]) == 0:
                graph = c.msg_no_values
            else:
                # Determination of the selected wtr on the graph.
                if (
                    ctx.triggered_id == "switch-bands"
                    or ctx.triggered_id == "switch-median"
                ):
                    wtr_id = last_selected_wtr  # If one of the switches has been activated, the selected wtr has not changed, so it is retrieved from the memory.
                elif selected_wtr and selected_wtr[0]:
                    wtr_id = clicked_wtr[0]["points"][0]["customdata"]

                # Creation of the information section for the selected water testing result.
                if wtr_id is not None:  # "wtr_id" value can be 0.
                    wtr_indice = [list(df.index).index(wtr_id)]
                    row = df.loc[wtr_id]

                    wtr_info_content = [
                        html.Div(
                            f"{row['site_code']} - {row['date_time'].strftime('%d %b %Y')}",
                            style={"text-align": "center"},
                        ),
                        html.Hr(className="my-2"),
                        html.Div(
                            [
                                (
                                    html.Div(
                                        f"Air temperature: {row['air_temperature']}",
                                        className="mt-1",
                                    )
                                    if row["air_temperature"]
                                    else None
                                ),
                                (
                                    html.Div(
                                        f"Current rainfall: {row['current_rainfall']}",
                                        className="mt-1",
                                    )
                                    if row["current_rainfall"]
                                    else None
                                ),
                                (
                                    html.Div(
                                        f"Last rainfall: {row['last_rainfall']}",
                                        className="mt-1",
                                    )
                                    if row["last_rainfall"]
                                    else None
                                ),
                                (
                                    html.Div(f"Wind: {row['wind']}", className="mt-1")
                                    if row["wind"]
                                    else None
                                ),
                                (
                                    html.Div(f"Sky: {row['sky']}", className="mt-1")
                                    if row["sky"]
                                    else None
                                ),
                                (
                                    html.Div(
                                        f"Water surface: {row['water_surface']}",
                                        className="mt-1",
                                    )
                                    if row["water_surface"]
                                    else None
                                ),
                                (
                                    html.Div(
                                        f"Appearance: {row['appearance']}",
                                        className="mt-1",
                                    )
                                    if row["appearance"]
                                    else None
                                ),
                                (
                                    html.Div(
                                        f"Surface slick: {row['surface_slick']}",
                                        className="mt-1",
                                    )
                                    if row["surface_slick"]
                                    else None
                                ),
                                (
                                    html.Div(
                                        f"Floating matter: {row['floating_matter']}",
                                        className="mt-1",
                                    )
                                    if row["floating_matter"]
                                    else None
                                ),
                                (
                                    html.Div(
                                        f"Suspended matter: {row['suspended_matter']}",
                                        className="mt-1",
                                    )
                                    if row["suspended_matter"]
                                    else None
                                ),
                            ],
                            className="fs-s",
                        ),
                    ]
                else:
                    wtr_indice = []

                # Creation of the new graph figure.
                fig = go.Figure(
                    data=go.Scatter(
                        x=df["date_time"],
                        y=df[parameter],
                        customdata=df.index,
                        hovertemplate="%{x}<br>%{y}"
                        + c.metric_units[parameter]
                        + "<extra></extra>",
                        mode="lines+markers",
                        marker={"size": 8},
                        selected_marker={"color": "red"},
                        selectedpoints=wtr_indice,
                        showlegend=False,
                        connectgaps=True,
                    ),
                    layout={
                        "xaxis": {"title": {"text": "Date"}},
                        "yaxis": {"title": {"text": c.metric_names[parameter]}},
                        "title": {
                            "text": f"{c.metric_names[parameter]}<br>{site_code} - {site_name}",
                            "x": 0.5,
                        },
                        "template": "simple_white",
                        "clickmode": "event+select",
                    },
                )

                # Addition of indicative lines to the graph figure if switches are selected.
                if switch_median:
                    fig.add_hline(
                        y=df[parameter].median(),
                        name="median",  # showlegend=True,
                        line_color="green",
                        layer="below",
                        opacity=1,
                        line_width=2,
                    )

                if switch_bands:
                    fig.add_hline(
                        y=np.percentile(df[parameter], 68),
                        name="68% band (upper)",  # showlegend=True,
                        line={"color": "orange", "dash": "dash"},
                        layer="below",
                        opacity=1,
                        line_width=2,
                    )
                    fig.add_hline(
                        y=np.percentile(df[parameter], 32),
                        name="68% band (lower)",  # showlegend=True,
                        line={"color": "orange", "dash": "dashdot"},
                        layer="below",
                        opacity=1,
                        line_width=2,
                    )

                # Creation of the graph from the figure.
                graph = dcc.Graph(
                    id={"type": "graph", "index": "graph"},
                    figure=fig,
                    config={
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["select2d", "lasso2d"],
                    },
                )

        return (
            graph,
            wtr_info_content,
            wtr_id,
            btn_dl_site_sheet_disabled,
            btn_dl_raw_data_disabled,
        )

    @app.callback(
        Output("download", "data"),
        [
            Input("button-dl-site-sheet", "n_clicks"),
            Input("button-dl-raw-data", "n_clicks"),
        ],
        [
            State("map", "selectedData"),
            State("switch-median", "value"),
            State("switch-bands", "value"),
        ],
        prevent_initial_call=True,
    )
    def download(
        btn_dl_site_sheet_clicked,
        btn_dl_raw_data_clicked,
        selected_site,
        switch_median,
        switch_bands,
    ):
        """
        TODO
        """

        # Loading dataframes.
        df_sites = f.get_df_sites()
        df_water_testing_results = f.get_df_water_testing_results()

        # Retrieving the code and name of the site selected on the map.
        site_code = selected_site["points"][0]["customdata"]
        site_name = df_sites.loc[
            df_sites["site_code"] == site_code, "site_name"
        ].to_numpy()[0]

        # Retrieving water testing results for the selected site.
        df = df_water_testing_results[
            df_water_testing_results["site_code"] == site_code
        ]

        # Creation of the raw data CSV file or site sheet based on the button clicked.
        if ctx.triggered_id == "button-dl-raw-data":
            dl = dcc.send_data_frame(
                df.to_csv, site_code + "_raw_data.csv", index=False
            )
        else:
            # TODO: we can customise here by opening a pop-up window and choosing the graphic we want (with checkboxes) + the option of displaying horizontal lines.

            fig = make_subplots(x_title="Date", rows=7, cols=1)

            fig.update_layout(
                title={"text": f"{site_code} - {site_name}", "x": 0.5},
                template="simple_white",
                height=1600,
                width=1000,
            )

            # Creation of a subplot for each parameter.
            for i, (parameter, parameter_name) in enumerate(c.metric_names.items()):
                df_tmp = df.dropna(subset=parameter)

                if len(df_tmp[parameter]) == 0:
                    fig.add_annotation(
                        text=f"No values available for {parameter_name}.",
                        row=i + 1,
                        col=1,
                        showarrow=False,
                        font_color="#6c757d",
                        align="center",
                    )
                    fig.update_xaxes(visible=False, row=i + 1, col=1)
                    fig.update_yaxes(visible=False, row=i + 1, col=1)
                else:
                    fig.append_trace(
                        go.Scatter(
                            x=df_tmp["date_time"],
                            y=df_tmp[parameter],
                            mode="lines+markers",
                            marker={"size": 8},
                            showlegend=False,
                            connectgaps=True,
                        ),
                        row=i + 1,
                        col=1,
                    )
                    # TODO replace label calls below (commented out) with
                    # annotation_text, annotation_position parameters
                    # see: https://plotly.com/python/horizontal-vertical-shapes/
                    if switch_median:
                        fig.add_hline(
                            y=df_tmp[parameter].median(),
                            row=i + 1,
                            col=1,
                            # label=dict(
                            #    text="median", textposition="end", font_color="green"
                            # ),
                            annotation_text='Median',
                            annotation_position='bottom right',
                            annotation_font_color='green',
                            line_color="green",
                            layer="below",
                            opacity=1,
                            line_width=2,
                        )

                    if switch_bands:
                        fig.add_hline(
                            y=np.percentile(df_tmp[parameter], 68),
                            row=i + 1,
                            col=1,
                            # label=dict(
                            #    text="68% band (upper)",
                            #    textposition="end",
                            #    font_color="orange",
                            # ),
                            annotation_text="68% band (upper)",
                            annotation_position='top left',
                            annotation_font_color='orange',
                            line={"color": "orange", "dash": "dash"},
                            layer="below",
                            opacity=1,
                            line_width=2,
                        )
                        fig.add_hline(
                            y=np.percentile(df_tmp[parameter], 32),
                            row=i + 1,
                            col=1,
                            # label=dict(
                            #    text="68% band (lower)",
                            #    textposition="end",
                            #    font_color="orange",
                            # ),
                            annotation_text="68% band (lower)",
                            annotation_position='bottom left',
                            annotation_font_color='orange',
                            line={"color": "orange", "dash": "dashdot"},
                            layer="below",
                            opacity=1,
                            line_width=2,
                        )
                        # TODO: review how to display horizontal line labels. If the horizontal lines are too close, the labels will overlap.

                    fig.update_yaxes(title_text=parameter_name, row=i + 1, col=1)

            # # Conversion of the figure into a PDF file.
            # Conversion of the figure into a HTML file.
            # path = f"assets/{site_code}_site_sheet.pdf"
            path = f"assets/{site_code}_site_sheet.html"
            # fig.write_image(path, format="pdf")
            fig.write_html(
                path,
            )
            dl = dcc.send_file(path)
            os.remove(path)

        return dl


# Exporting a figure in PDF does not work with the latest version of Kaleido on Windows, so we need a specific version.
# https://community.plotly.com/t/static-image-export-hangs-using-kaleido/61519/2
# https://github.com/plotly/Kaleido/issues/126
