import pandas as pd

# import pyodbc
import datetime


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
