from plotly import graph_objects as go
import pandas as pd
import numpy as np

# need html to build text in introductory container
from dash import html

# import pyodbc
import re

import os

from utils.sql_excel import (
    read_results_from_excel,
    read_sites_from_excel,
    get_sites_sql,
    get_water_testing_results_sql,
)

pd.set_option("display.max_rows", None)


def set_df_water_testing_results():
    """
    Returns the water testing results dataframe.

    :return: the water testing results dataframe containing, in order, the following columns :
        - code of the site where the measurements were taken        (column : site_code [unique identifier])
        - date and time the measurements were taken                 (column : date_time)
        - equipment with which the measurements were taken          (column : equipment_id)
        - water testing results for various parameters              (columns : temperature, ph, conductivity, turbidity, dissolved_oxygen, dissolved_oxygen_percentage, salinity)
        - environmental conditions during water testing             (columns : air_temperature, current_rainfall, last_rainfall, wind, sky, water_surface, water_level, flow, appearance, surface_slick, floating_matter, suspended_matter)
    :rtype: pd.DataFrame
    """

    # with open('utils/data/df_water_testing_results.txt', 'w') as f:
    #    df_string = get_water_testing_results().to_string(index=False)
    #    f.write(df_string)
    get_water_testing_results().to_feather(
        "./utils/data/df_water_testing_results.feather"
    )


def get_df_water_testing_results():
    """Updates the water testing results dataframe file"""

    return pd.read_feather("./utils/data/df_water_testing_results.feather")


def set_df_sites():
    """
    Returns the site dataframe.

    :return: the site dataframe containing, in order, the following columns :
        - site code                                 (column : site_code [unique identifier])
        - site name                                 (column : site_name)
        - geographical coordinates of the site      (columns : latitude, longitude)
        - status of site measurements               (column : status)
        - site waterway                             (column : waterway)
        - site waterbody                            (columns : waterbody_type, waterbody_code)
    :rtype: pd.DataFrame
    """

    # with open('utils/data/df_sites.txt', 'w') as f:
    #    df_string = get_sites(get_df_water_testing_results()).to_string(index=False)
    #    f.write(df_string)

    get_sites(get_df_water_testing_results()).to_feather(
        "./utils/data/df_sites.feather"
    )


def get_df_sites():
    """Updates the site dataframe file"""

    return pd.read_feather("./utils/data/df_sites.feather")


def set_dfs():
    """Updates all dataframe files"""

    set_df_water_testing_results()  # Must be executed first because the "set_df_sites()" function uses the result of this function.
    set_df_sites()


def get_conn():
    DB_PATH = "utils/data/Community Water Monitoring Database - Aug 2023.accdb"

    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        r"DBQ=" + DB_PATH  # chemin relatif si possible et nom standard pour la bd
    )

    return pyodbc.connect(conn_str)


def get_water_testing_results():
    # sql = """
    #     SELECT
    #         [Site Code] AS site_code,
    #         DateSampleTaken AS date_time,
    #         TimeSampleTaken AS time_tmp,
    #         [Equipment ID] AS equipment_id,
    #         [Water Temp (°C)] AS temperature,
    #         [Ph (pH Units)] AS ph,
    #         [Conductivity (mS/cm)] AS conductivity,
    #         [Turbidity (NTU)] AS turbidity,
    #         [Dissolved Oxygen (mg/L)] AS dissolved_oxygen,
    #         [Dissolved Oxygen (%)] AS dissolved_oxygen_percentage,
    #         [Salinity (%)] AS salinity,
    #         [Air Temperature] AS air_temperature,
    #         [Current Rainfall] AS current_rainfall,
    #         [Last Rainfall] AS last_rainfall,
    #         wind,
    #         sky,
    #         [Water Surface] AS water_surface,
    #         [Water Level] AS water_level,
    #         flow,
    #         appearance,
    #         [Surface Slick] AS surface_slick,
    #         [Floating Matter] AS floating_matter,
    #         [Suspended Matter] AS suspended_matter
    #     FROM Results_Sites_Water_Testing;
    # """

    # cnxn = get_conn()
    # df = pd.read_sql(sql, cnxn)
    # cnxn.close()

    # df = get_water_testing_results_sql()
    df = read_results_from_excel()

    # Deletion of measurement points without a site or date.
    df = df.dropna(subset=["site_code", "date_time"])

    # drop rows with bad dates or times (known prob as at 20041129)
    # Pandas will set value to NaT (not a time) on failure to parse
    df["date_check"] = pd.to_datetime(
        df['date_time'],
        errors="coerce",
        dayfirst=True,
    )
    df = df.dropna(subset=["date_check"])

    df["time_check"] = pd.to_datetime(
        df['time_tmp'],
        errors="coerce",
        dayfirst=True,
    )
    df = df.dropna(subset=["time_check"])

    # drop rows with dates in the future (known prob as at 20041129)
    df = df[df["date_check"] <= pd.Timestamp.today()].copy()

    # drop rows with dates before 2000 (known prob as at 20041129)
    df = df[df["date_check"] > pd.Timestamp(year=2000, month=1, day=1)].copy()

    # Grouping date and time columns.
    df["date_time"] = pd.to_datetime(
        df.date_check.dt.date.astype(str)
        + " "
        + df.time_check.fillna(pd.Timestamp(0)).dt.time.astype(str)
    )
    df = df.drop(columns=["time_tmp"])

    # Harmonisation of site codes.
    df["site_code"] = df["site_code"].str.upper()  # 'Pay105', 'PEt649', ...
    df["site_code"] = df["site_code"].str.replace(" ", "")  # 'PAY 220', 'PET 320', ...

    # Deletion of measurement points where there are not enough to create a graph.
    nb_row = df.value_counts("site_code")
    sites_ok = nb_row[nb_row > 3].index.tolist()
    df = df[df["site_code"].isin(sites_ok)]

    # Selection of sites with >= 365 days between first and last reading
    # this could be a list comprehension, but clearer I feel as an append loop
    sites_ok = []
    for site in sorted(df["site_code"].unique()):
        d1 = df[df["site_code"] == site]["date_time"].max()
        d2 = df[df["site_code"] == site]["date_time"].min()
        delta = d1 - d2
        if delta.days >= 365:
            sites_ok.append(site)
        # end if
    # end for

    # as per email from Teveor Morrison Dec 2 2024, adding MTN105, MTN110 as exceptions to >365 days rule
    # (used for public demonstration purposes) Currently (20250101), neither site has a lat/lon in sites table
    sites_ok.append("MTN110")
    sites_ok.append("MTN105")

    # select out good sites
    df = df[df["site_code"].isin(sites_ok)]

    # Deletion of duplicate letters at the beginning of descriptive words (C-Cold, L-Light, F-Flat, ...).
    df["air_temperature"] = [
        re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["air_temperature"]
    ]
    df["current_rainfall"] = [
        re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["current_rainfall"]
    ]
    df["last_rainfall"] = [
        re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["last_rainfall"]
    ]
    df["wind"] = [re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["wind"]]
    df["sky"] = [re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["sky"]]
    df["water_surface"] = [
        re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["water_surface"]
    ]
    df["water_level"] = [
        re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["water_level"]
    ]
    df["flow"] = [re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["flow"]]
    df["appearance"] = [
        re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["appearance"]
    ]
    df["surface_slick"] = [
        re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["surface_slick"]
    ]
    df["floating_matter"] = [
        re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["floating_matter"]
    ]
    df["suspended_matter"] = [
        re.sub(r"^([A-Za-z])-\1", r"\1", str(x)) for x in df["suspended_matter"]
    ]

    # Deletion of 'nil' and 'none' strings.
    df = df.replace("(?i)nil", "", regex=True)
    df = df.replace("(?i)none", "", regex=True)

    df = df.sort_values(["site_code", "date_time"]).reset_index(drop=True)

    return df


def get_sites(df_water_testing_results):
    # sql = """
    #     SELECT
    #         [Site Code] AS site_code,
    #         [Site Name] AS site_name,
    #         latitude,
    #         longitude,
    #         status,
    #         waterway,
    #         [Waterbody Type] AS waterbody_type,
    #         [Water Code] AS waterbody_code
    #     FROM Sites;
    # """

    # cnxn = get_conn()
    # df = pd.read_sql(sql, cnxn)
    # cnxn.close()

    # df = get_sites_sql()
    df = read_sites_from_excel()

    # Conversion of latitude and longitude into floating values.
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    # correct positive latitude
    df["latitude"] = -df["latitude"].abs()

    # Deletion of points without latitude or longitude.
    df = df.dropna(subset=["latitude", "longitude"])

    # We only keep sites for which we have water testing results.
    df = df[df["site_code"].isin(df_water_testing_results["site_code"])]

    df = df.sort_values("site_code").reset_index(drop=True)

    return df


def get_map_figure(df_sites, selected_site_code=None, layout=None):
    # The 'go.Scattermapbox' object needs an indice for its 'selectedpoints' property, so we retrieve the indice for the site selected in the dataframe.
    # From https://plotly.com/python-api-reference/generated/plotly.graph_objects.Scattermapbox.html:
    #   selectedpoints – Array containing integer indices of selected points. Has an effect only for traces that support selections.
    #   Note that an empty array means an empty selection where the unselected are turned on for all points, whereas, any other non-array values means no selection all where the selected and unselected styles have no effect.
    if selected_site_code and selected_site_code in df_sites["site_code"].values:
        selected_site_indice = [list(df_sites["site_code"]).index(selected_site_code)]
    else:
        selected_site_indice = []

    fig = go.Figure(
        go.Scattermapbox(
            lat=df_sites["latitude"],
            lon=df_sites["longitude"],
            customdata=list(df_sites["site_code"]),
            text=list(df_sites["status"]),
            hovertemplate="<b>Site:</b> %{customdata}<br><b>Status:</b> %{text}<extra></extra>",
            marker={"size": 8},
            selected_marker={"color": "red"},
            selectedpoints=selected_site_indice,  # We only allow the selection of a single point, so the 'selected_point' array must contain none or one value.
        )
    )

    if not layout:
        fig.layout = go.Layout(
            mapbox_style="open-street-map",
            mapbox_center={
                "lat": (df_sites["latitude"].min() + df_sites["latitude"].max()) / 2,
                "lon": (df_sites["longitude"].min() + df_sites["longitude"].max()) / 2,
            },
            mapbox_zoom=9,
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            clickmode="event+select",
        )
    else:
        fig.layout = layout

    return fig

#end  get_map_figure

def group_by_period(df: pd.DataFrame):
    '''
    group_by_period: assign a group integer to each row, which increments across big time gaps

    assumes the date-time is stored in column ["date_time"]
    time gap is half a year ~ 180 days
    '''

    group_no = 1
    df['group'] = group_no

    MAX_DAYS_GAP = 180  # ~ 6 months

    for i, i_prev in zip(df.index[1:], df.index[0 : len(df) - 1]):

        if (df.loc[i, "date_time"] - df.loc[i_prev, "date_time"]) > pd.Timedelta(
            value=MAX_DAYS_GAP, unit='D'
        ):
            # have big gap in sample taken dates, so assign to a new group
            group_no = group_no + 1
            df.loc[i:, 'group'] = group_no
        # end if
    # end for

    return None


# end group_by_period

def drop_outliers(df, parameter):
    '''
    drop_outliers: drop rows that have an outlier value for parameter

    assumes df is a pandas dataframe, and the array of interest is df[parameter]

    Returns:
    None

    Side Effects: may drop rows from dataframe

    '''

    # filter out exterme values from plot
    # parameter is set to column name of physical quantity currently being processed
    EXTREME = 5
    TOO_SMALL = 0.1
    avg = df[parameter].median()
    std = df[parameter].std()

    # if std is not too small (eg salinity all zero) remove outliers
    if std > TOO_SMALL:
        for i, v in zip(df.index, df[parameter]):
            delta = np.abs(v - avg) / std
            if delta > EXTREME:
                # drop the row, so it wont be added to line plot
                df.drop(index=i, inplace=True)
            # end if
        # end for
    # end if


# end drop_outliers

# function tom return intrtoductory text as dash  objects

def get_intro_text():
    return [
        html.H3("Overview"),
        html.P(
            '''
                    Originally commencing in 1993 under ECOllaboration's prior organisational 
                    name 'Maroochy Waterwatch', the water monitoring program has amassed a large 
                   collection of water quality data from a range of locations 
                   within the Maroochy River catchment.  Key subcatchments included in this 
                   dataset derive from various sites along Petrie Creek, Paynter’s Creek, 
                   Stumer’s Creek, Eudlo Creek, Cornmeal Creek, Maroochy River and many other 
                   smaller connecting tributaries. In its 33rd consecutive year, 
                   the water monitoring program is believed to be the longest ongoing 
                   citizen science project in Queensland and is a testament to both our 
                   past and present dedicated volunteer team, supported by the community 
                   engagement team at ECOllaboration. 
                   Digital records within this dataset stretch back to 2011 with archived 
                   paper copies prior to this date yet to be processed into digital formats 
                   but will be added in due course. 
                   '''
        ),
        html.H3('Method'),
        html.P(
            '''
                    Using ECOllaboration's set of 6 x Horiba U-52 multi probe analysers, 
                   our trained volunteer community network tests up to 50 sites across the 
                   Sunshine Coast each month. Citizen science data (including turbidity, 
                   dissolved oxygen, and salinity levels) is collected, analysed and then 
                   stored for assessment to assist with any initial concerns reported through 
                   to Sunshine Coast Council relating to water quality conerns. Each water 
                   monitoring kit is calibrated monthly to ensure data accuracy and all quality 
                   assurance procedures have been developed in conjunction with the Department 
                   of Environmental and Resource Management (DERM).
                    '''
        ),
        html.H3('Acknowledgments '),
        html.P(
            '''
                    This new interactive website has been produced as a private prototype model only, 
                   pending public release in late 2025. Developed by volunteer Don Cameron (2024 
                   ECOllaboration Water Monitoring Volunteer of the Year) in liaison with Trevor 
                   Morrison (ECOllaboration Community Development Manager), the aim of this prototype 
                   is to provide volunteers with interactive access to the large dataset. '''
        ),
        html.P(
            '''
                   A special acknowledgement to William Masson who, while undertaking his Cert I in 
                   Conservation and Ecosystem Management, took the initiative to utilise his existing 
                   data visualisation skills and begin the coding process for Don to later finalise.  
                   ECOllaboration also wishes to thank Thomas Klinger, who has volunteered his time 
                   for many years entering the data each month into our large digital database.
                   We think this project is a wonderful example of volunteers, trainees and staff 
                   working together for the benefit of our local community. '''
        ),
        html.P(
            '''
                   Volunteers are encouraged to provide feedback to Trevor at trevor@ecollaboration.org.au 
                   for any data queries/missing sites etc. ECOllaboration would like to thank Don 
                   Cameron for making this tool available, and to all of our volunteers for their 
                   valuable contributions to this dataset. 
                   Sunshine Coast Council proudly supports the water monitoring initiative through their grants program.
                   '''
        ),
    ]
# end get_intro_text
