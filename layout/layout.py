from dash import dcc, html
import dash_bootstrap_components as dbc
import utils.functions as f
import utils.constants as c


def layout():

    df_sites = f.get_df_sites()

    return dbc.Container([

        # button for hid/show on introductory text
        html.Div(
            [
                html.Button('Introduction Hide/Show', id='show_hide'),
                html.Div(id='contents-container'),
           ]
        ),
        #
        #
        #

        dbc.Row([

            # # #  SITE INFO SECTION  # # #
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Community Water Quality Monitoring'),
                    dbc.CardBody([
                        html.Div('Site filters'),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label('Status', html_for='dropdown-status', class_name='mb-1'), 
                                dbc.Select(
                                    id='dropdown-status',
                                    options=[
                                        {'label': 'All', 'value': 'all'},
                                        {'label': 'Current', 'value': 'Current'},
                                        {'label': 'Previous', 'value': 'Previous'}
                                    ],
                                    value='all'
                                )
                            ]),
                            dbc.Col([
                                dbc.Label('Waterway', html_for='dropdown-waterway', class_name='mb-1'), 
                                dbc.Select(
                                    id='dropdown-waterway',
                                    options=[{'label': 'All', 'value': 'all'}] + [{'label': ww, 'value': ww} for ww in sorted(df_sites['waterway'].unique())],
                                    value='all'
                                )
                            ])
                        ]),
                        html.Hr(),
                        html.Div(c.msg_no_site, id='container-site-info')
                    ])
                ], className='text-center')
            ], width=4),

            # # #  MAP SECTION  # # #
            dbc.Col([
                dcc.Graph(
                    id='map',
                    figure=f.get_map_figure(df_sites),
                    config={
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d']
                    },
                    style={'height': '400px'}
                ),
                dcc.Store(id='mem-selected-site')
            ], width=8)

        ], className='mb-3 mt-2'),

        dbc.Row([

            # # #  GRAPH PARAMETERS SECTION  # # #
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Graph parameters', className='text-center'),
                    dbc.CardBody([
                        dbc.Select(
                            id='dropdown-parameter',
                            options=[
                                {'label': c.metric_names['temperature'], 'value': 'temperature'},
                                {'label': c.metric_names['ph'], 'value': 'ph'},
                                {'label': c.metric_names['conductivity'], 'value': 'conductivity'},
                                {'label': c.metric_names['turbidity'], 'value': 'turbidity'},
                                {'label': c.metric_names['dissolved_oxygen'], 'value': 'dissolved_oxygen'},
                                {'label': c.metric_names['dissolved_oxygen_percentage'], 'value': 'dissolved_oxygen_percentage'},
                                {'label': c.metric_names['salinity'], 'value': 'salinity'}
                            ],
                            value='temperature',
                            className='mb-2'
                        ),
                        dbc.Checklist(
                            options=[
                            #{'label': 'Median', 'value': 1}
                                                    {
                                                        'label': html.Span(
                                                            "Median",
                                                            id="tooltip-target1",
                                                            style={
                                                                "textDecoration": "underline",
                                                                "cursor": "pointer",
                                                            },
                                                        ),
                                                        'value': 1,
                                                    }
                            ],
                            value=[],
                            id='switch-median',
                            switch=True,
                        ),
                        dbc.Tooltip(
                                                "Median: approximately half of readings will be above median line, half below"
                                                " (excluding outliers)",
                                                target='tooltip-target1',
                                            ),
                        dbc.Checklist(
                            options=[
                            #{'label': '68% band', 'value': 1}
                            {
                                                        'label': html.Span(
                                                            "68% band",
                                                            id="tooltip-target2",
                                                            style={
                                                                "textDecoration": "underline",
                                                                "cursor": "pointer",
                                                            },
                                                        ),
                                                        'value': 1,
                            }
                            ],
                            value=[],
                            id='switch-bands',
                            switch=True,
                        ),
                        dbc.Tooltip(
                                                "68% band: approximately 68% of readings will be between these two lines"
                                                " (excluding outliers)",
                                                target='tooltip-target2',
                        ),
                        html.Hr(),
                        html.Div([
                            html.Div('Downloads', className='mb-2'),
                            dbc.Spinner([
                                dbc.Button(
                                    [html.I(className='bi bi-file-earmark me-1'), 'Site sheet'],
                                    id='button-dl-site-sheet',
                                    disabled=True,
                                    color='secondary',
                                    className='m-1'
                                ), 
                                dbc.Button(
                                    [html.I(className='bi bi-database me-1'), 'Raw data'],
                                    id='button-dl-raw-data',
                                    disabled=True,
                                    color='secondary',
                                    className='m-1'
                                ),
                                dcc.Download(id='download')
                            ], delay_show=500)
                        ], className='text-center')
                    ])
                ])
            ], width=2),

            # # #  GRAPH SECTION  # # #
            dbc.Col(c.msg_no_graph, id='container-graph', width=8),

            # # #  ENVIRONMENTAL CONDITIONS SECTION  # # #
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader('Environmental conditions', className='text-center'),
                    dbc.CardBody(c.msg_no_point, id='container-wtr-info'),
                    dcc.Store(id='mem-selected-wtr')
                ])
            ], width=2)

        ]),
        # footer with logos and copyright notice
        dbc.Row(
                [
                    html.Hr(),
                    dbc.Col(
                        [
                            html.Img(
                                src=r'assets/eco-logo.jpg',
                                alt='ECO Logo',
                                style={'height': '82px', 'width': '180px'},
                            ),
                        ]
                    ),
                    dbc.Col(
                        [
                            html.P(
                                    "Copyright 2024 ECOllaboration | All Rights Reserved",
                                     style={"font-size": "x-small"},
                                    ),
                        ]
                   ),
                    dbc.Col(
                        [
                            html.Img(
                                src=r'assets/scc-logo.png',
                                alt='SCC Logo',
                                style={'height': '82px', 'width': '180px'},
                            ),
                        ]
                    ),
                ]
        ),

    ], fluid=True)
