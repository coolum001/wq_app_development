import pandas as pd

# import pyodbc
import datetime

#  add functions to perform ad hoc repair to  correct
#  errors  in database.  These may be corrected at some later time
#   but  performing these corrections will  be harmless


def adhoc_sites_repair(df):
    """
    adhoc_sites_repair: One off function to fix error in database table sites

    Parameters:
    df: pandas dataframe holding sites data, with columns 'site_code', 'latitude', 'longitude' 'waterway'

    Returns:
    update dataframe with corrected latitudes and longitudes for sites PAY220, PAY600, WHA390, EUD585
    corrected waterway for sites with site code starting with 'WHA'

    Notes:  this function should NOT cause problems if these fixes are no longer needed

    """

    df['latitude'] = df['latitude'].where(df['site_code'] != 'PAY220', -26.685945)
    df['longitude'] = df['longitude'].where(df['site_code'] != 'PAY220', 152.949373)

    df['latitude'] = df['latitude'].where(df['site_code'] != 'PAY600', -26.646699)
    df['longitude'] = df['longitude'].where(df['site_code'] != 'PAY600', 152.983393)

    df['latitude'] = df['latitude'].where(df['site_code'] != 'WHA390', -26.630176)
    df['longitude'] = df['longitude'].where(df['site_code'] != 'WHA390', 152.9544)

    df['latitude'] = df['latitude'].where(df['site_code'] != 'EUD585', -26.665079)
    df['longitude'] = df['longitude'].where(df['site_code'] != 'EUD585', 153.012656)

    df['waterway'] = df['waterway'].where(
        df['site_code'].str[0:3] != 'WHA', "Whalley Creek"
    )

    return df


# end adhoc_sites_repair


def adhoc_results_repair(df):
    """
    adhoc_results_repair: One off function to fix error in database table results

    Parameters:
    df: pandas dataframe holding results data, with columns 'site_code',

    Returns:
    update dataframe with WHA548 site codes to WHA390 in all places they occur


    Notes:  this function should NOT cause problems if these fixes are no longer needed

    """

    df['site_code'] = df['site_code'].where(df['site_code'] != 'WHA548', 'WHA390')

    # "I agree with your judgement that all readings should be removed prior to 2018 to ensure data maintains overall credibility. ""
    # T Morrison email Apr 10, 2026,

    df["dissolved_oxygen_percentage"] = df["dissolved_oxygen_percentage"].where(
        df["date_time"] > pd.Timestamp(year=2018, month=1, day=1), 0.0
    )

    return df


# end adhoc_results_repair


def read_results_from_excel():
    URL = "utils/data/waterqualityspreadsheet.xlsx"

    SS_TAB = "Results_Sites_Water_Testing"

    df = pd.read_excel(
        URL,
        sheet_name=SS_TAB,
        header=0,
        usecols=[
            "Site Code",
            "DateSampleTaken",
            "TimeSampleTaken",
            "Equipment ID",
            "Water Temp (°C)",
            "Ph (pH Units)",
            "Conductivity (mS/cm)",
            "Turbidity (NTU)",
            "Dissolved Oxygen (mg/L)",
            "Dissolved Oxygen (%)",
            "Salinity (%)",
            "Air Temperature",
            "Current Rainfall",
            "Last Rainfall",
            "Wind",
            "Sky",
            "Water Surface",
            "Water Level",
            "Flow",
            "Appearance",
            "Surface Slick",
            "Floating Matter",
            "Suspended Matter",
        ],
    )

    rename_dict = {
        "Site Code": "site_code",
        "DateSampleTaken": "date_time",
        "TimeSampleTaken": "time_tmp",
        "Equipment ID": "equipment_id",
        "Water Temp (°C)": "temperature",
        "Ph (pH Units)": "ph",
        "Conductivity (mS/cm)": "conductivity",
        "Turbidity (NTU)": "turbidity",
        "Dissolved Oxygen (mg/L)": "dissolved_oxygen",
        "Dissolved Oxygen (%)": "dissolved_oxygen_percentage",
        "Salinity (%)": "salinity",
        "Air Temperature": "air_temperature",
        "Current Rainfall": "current_rainfall",
        "Last Rainfall": "last_rainfall",
        "Water Surface": "water_surface",
        "Water Level": "water_level",
        "Surface Slick": "surface_slick",
        "Floating Matter": "floating_matter",
        "Suspended Matter": "suspended_matter",
        "Wind": "wind",
        "Sky": "sky",
        "Flow": "flow",
        "Appearance": "appearance",
    }

    df = df.rename(
        columns=rename_dict,
    )
    #
    # convert time column to be compatable with SQL sourced column

    # first, get rid of nulls
    time_zero = datetime.time(hour=0, minute=0, second=0)

    df['time_tmp'] = df['time_tmp'].fillna(value=time_zero)

    # now convert to pandas Timestamps.  Note
    # we only use time part of this column, so put in start of epoch year
    df['time_tmp'] = [
        pd.Timestamp(
            year=1970, month=1, day=1, hour=x.hour, minute=x.minute, second=x.second
        )
        for x in df['time_tmp']
    ]

    # fix know defects in database results table
    df = adhoc_results_repair(df)

    return df


# end read_results_from_excel


def read_sites_from_excel():
    URL = "utils/data/waterqualityspreadsheet.xlsx"

    SS_TAB = "Sites"

    df = pd.read_excel(
        URL,
        sheet_name=SS_TAB,
        header=0,
        usecols=[
            "Site Code",
            "Site Name",
            "Latitude",
            "Longitude",
            "Status",
            "Waterway",
            "Waterbody Type",
            "Water Code",
        ],
    )

    rename_dict = {
        "Site Code": 'site_code',
        "Site Name": 'site_name',
        "Latitude": 'latitude',
        "Longitude": 'longitude',
        "Status": 'status',
        "Waterway": 'waterway',
        "Waterbody Type": 'waterbody_type',
        "Water Code": 'waterbody_code',
    }

    df = df.rename(
        columns=rename_dict,
    )

    # fix errors in sites datatable

    df = adhoc_sites_repair(df)

    return df


# end read_sites_from_excel


def get_conn():
    DB_PATH = r"C:\Users\donrc\Documents\VisualCodeProjects\DashMapExcelProject\utils\data\Community Water Monitoring Database - Aug 2023.accdb"

    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        r"DBQ=" + DB_PATH  # chemin relatif si possible et nom standard pour la bd
    )

    return pyodbc.connect(conn_str)


# end get_conn


def get_sites_sql():
    sql = """
        SELECT
            [Site Code] AS site_code, 
            [Site Name] AS site_name, 
            latitude, 
            longitude, 
            status, 
            waterway, 
            [Waterbody Type] AS waterbody_type, 
            [Water Code] AS waterbody_code 
        FROM Sites;
    """

    cnxn = get_conn()
    df = pd.read_sql(sql, cnxn)
    cnxn.close()
    return df


# end get_sites_sql


def get_water_testing_results_sql():
    sql = """
        SELECT
            [Site Code] AS site_code, 
            DateSampleTaken AS date_time, 
            TimeSampleTaken AS time_tmp,
            [Equipment ID] AS equipment_id, 
            [Water Temp (°C)] AS temperature, 
            [Ph (pH Units)] AS ph, 
            [Conductivity (mS/cm)] AS conductivity, 
            [Turbidity (NTU)] AS turbidity, 
            [Dissolved Oxygen (mg/L)] AS dissolved_oxygen, 
            [Dissolved Oxygen (%)] AS dissolved_oxygen_percentage, 
            [Salinity (%)] AS salinity,
            [Air Temperature] AS air_temperature,
            [Current Rainfall] AS current_rainfall,
            [Last Rainfall] AS last_rainfall,
            wind,
            sky,
            [Water Surface] AS water_surface, 
            [Water Level] AS water_level, 
            flow,
            appearance,
            [Surface Slick] AS surface_slick,
            [Floating Matter] AS floating_matter,
            [Suspended Matter] AS suspended_matter
        FROM Results_Sites_Water_Testing;
    """

    cnxn = get_conn()
    df = pd.read_sql(sql, cnxn)
    cnxn.close()
    return df


# end get_water_testing_results_sql
