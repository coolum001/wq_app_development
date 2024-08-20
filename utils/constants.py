from dash import html

metric_names = {
    'temperature': 'Water Temp (°C)',
    'ph': 'Ph (pH Units)',
    'conductivity': 'Conductivity (mS/cm)',
    'turbidity': 'Turbidity (NTU)',
    'dissolved_oxygen': 'Dissolved Oxygen (mg/L)',
    'dissolved_oxygen_percentage': 'Dissolved Oxygen (%)',
    'salinity': 'Salinity (%)'
}

metric_units = {
    'temperature': ' °C',
    'ph': ' pH Units',
    'conductivity': ' mS/cm',
    'turbidity': ' NTU',
    'dissolved_oxygen': ' mg/L',
    'dissolved_oxygen_percentage': '%',
    'salinity': '%'
}

msg_no_site = html.Div('Select a site to view information.', className='text-muted')
msg_no_graph = html.Div('Select a site to view a graph.', className='mt-5 text-muted', style={'text-align': 'center'})
msg_no_values = html.Div('No values available for this metric.', className='mt-5 text-muted', style={'text-align': 'center'})
msg_no_point = html.Div('Select a site then a point on it to view point infos.', className='text-muted', style={'text-align': 'center'})