import pandas as pd
import os
home = os.path.dirname(__file__) 

def get_table_dict(calc_water_year=True, et_corrected=False):
    """
    Loads the csv data and return a dict with catchment id as key and a dataframe as value
    """
    
    matQ = pd.read_csv(home + os.sep + 'dis_mm_1991_2018.csv', delimiter=';', parse_dates=[0], index_col=0, dayfirst=True)
    if et_corrected:
        matE = pd.read_csv(home + os.sep + 'et_mm_1991_2018_corrected.csv', delimiter=';', parse_dates=[0], index_col=0, dayfirst=True)
    else:
        matE = pd.read_csv(home + os.sep + 'et_mm_1991_2018_uncorrected.csv', delimiter=';', parse_dates=[0], index_col=0, dayfirst=True)
    matP = pd.read_csv(home + os.sep + 'prec_mm_1991_2018.csv', delimiter=';', parse_dates=[0], index_col=0, dayfirst=True)


    dataframes = {}

    for catch in matE.columns:
        df = pd.DataFrame()
        df['Q'] = matQ[catch]
        df['E'] = matE[catch]
        df['P'] = matP[catch]
        if calc_water_year:
            water_year(df)
        dataframes[int(catch)] = df

    return dataframes


def water_year(df:pd.DataFrame):
    """
    Adds a column to a dataframe (with datetime index) with the hydrological year 
    , hydrological day and hydrological month
    """
    df["water_year"] = (df.index + pd.DateOffset(months=2)).year
    days_water_year = []
    for i, (year, year_df) in enumerate(df.groupby("water_year")):
        if i == 0:
            days_of_last_year = 30 + 31 # November plus December
            days_water_year += list(range(1 + days_of_last_year, year_df.shape[0]+1 + days_of_last_year))
        else:
            days_water_year += list(range(1, year_df.shape[0]+1))
    df["day_of_water_year"] = days_water_year
    def shift_month(month):
        if month == 11:
            return 1
        elif month == 12:
            return 2
        else:
            return month + 2
    df["month_of_water_year"] = list(map(shift_month, list(df.index.month)))


def translate_catchment_attributes(attributes):
    """
    Translates the catchment attributes from their German names to English.
    """
    attributes.rename(columns={"dominating_soil_type_bk500":"Soil Type [/]", 
                               "leitercharackter_huek250":"Aquifer Conductivity [/]",
                               "gesteinsart_huek250":"Geology Type [/]",
                               "soil_texture_boart_1000": "Soil Texture [/]",
                               "durchlässigkeit_huek250":"Permeability [/]",
                               "land_use_corine":"Land Use [/]",
                               "area_m2_watershed":"Area [km²]",
                               "grundwasserneubildung_gwn_1000": "Ground Water Recharge [mm]",
                               "greundigkeit_physgru_1000":"Soil Depth [m]",
                               "slope_mean_dem_40":"Slope [/]",
                               "elongation_ratio":"Elongation Ratio [/]",
                               "et_mean":"Act. Evapotranspiration [mm]",
                               "dis_mean":"Discharge [mm]",
                               "prec_mean":"Precipitation [mm]",
                               "runoff_ratio":"Runoff-Ratio [/]"},
                        inplace=True)
    attributes["Soil Type [/]"].replace({'Dystric_Cambisols':"DC",
       'Haplic_Luvisols_/_Eutric_Podzoluvisols_/_Stagnic_Gleysols_':"HL/EP/SG",
       'Eutric_Cambisols' :"EC",
       'Spodic_Cambisols' :"SC",
       'Eutric_Cambisols_/_Stagnic_Gleysols':"EC/SG", 
       'Dystric_Cambisols_':"DC",
       'Spodic_Cambisol_':"SC", 
       'Eutric_Cambisols_/_Stagnic_Gleysols_':"EC/SG"}, inplace=True)
    attributes["Aquifer Conductivity [/]"].replace({
            'Grundwasser-Geringleiter': "low", 
            'Grundwasser-Leiter': "normal",
            'Grundwasser-Leiter/Geringleiter':"normal/low"}, inplace=True)
    attributes["Geology Type [/]"].replace({
            'Sediment' : "sedimentary", 
            'Magmatit': "igneous" },inplace=True)
    attributes["Soil Texture [/]"].replace({
            'Lehmsande (ls)': "loamy sand", 
            'Tonschluffe (tu)':"clay silt", 
            'Sandlehme (sl)': "sandy loam",       
            'Schlufftone (ut)': "silty clay", 
            'Lehmschluffe (lu)': "loamy silt"},inplace=True)
    attributes["Permeability [/]"].replace({
            'gering (>1E-7 - 1E-5)': "low", 
            'mittel bis maessig (>1E-5 - 1E-3)':"mid/moderate",
            'maessig (>1E-5 - 1E-4)':"moderate", 
            'gering bis aeußerst gering (<1E-5)':"low/very low",
            'maessig bis gering (>1E-6 - 1E-4)':"moderate/low", 
            'sehr gering (>1E-9 - 1E-7)':"very low",
            'stark variabel':"variable", 
            'mittel (>1E-4 - 1E-3)':"mid"}, inplace=True)
    return attributes


def translate_year_attributes(years):
    years.rename(columns={
            'et_mm_1991_2018_corrected': "Act. Evapotranspiration [mm]", 
            'prec_mm_1991_2018': "Precipitation [mm]", 
            'most_rain_one_day': "Max Prec. Day [mm]",       
            'most_rain_one_month': "Max Prec. Month [mm]", 
            'rainfall_seasonality' : "Rainfall Seasonality [/]", 
            'snow_fraction': "Snow Fraction [%]",
            'aridity':"Aridity [/]"},inplace=True)
    return years
    


def get_attributes_catchments():
    attributes = pd.read_csv(home + os.sep + 'cleaned_catchment_attributes_num.csv', delimiter=';', index_col=0)
    attributes.drop(["gauge"], inplace=True,axis=1)

    attributes["dominating_soil_type_bk500"] = attributes["dominating_soil_type_bk500"].str.replace(" ", "_")
    attributes["area_m2_watershed"] = attributes["area_m2_watershed"] / 1000000
    attributes = translate_catchment_attributes(attributes)
    return attributes

def get_attributes_years():
    years = pd.read_csv(home + os.sep + 'cleaned_year_attributes.csv', delimiter=';', index_col=0)
    years = translate_year_attributes(years)
    return years

if __name__ == "__main__":
    #dataframes = get_table_dict(calc_water_year=True)
   # attributes = get_attributes_catchments()
   years = get_attributes_years()