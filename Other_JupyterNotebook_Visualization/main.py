import sys
from datetime import datetime
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.plotly as py
import plotly.graph_objs as go


def load_clean_eu_emissions():
    """Function to load and cleanse the EU emissions data."""

    # Define the EU emissions file name
    eu_em_file = './Pollution_Data/eu_emissions.csv'

    # Import the EU emissions data file into a dataframe
    eu_emissions = pd.read_csv(eu_em_file)

    # Drop unnecessary columns
    eu_emissions = eu_emissions.drop(['Country_Code', 'Format_name',
        'Sector_code', 'Emissions_Gg', 'Unit', 'Notations'], axis=1)

    # Convert column names to lower case
    eu_emissions.columns = eu_emissions.columns.str.lower()

    # Drop rows where the value is NaN
    eu_emissions = eu_emissions.dropna(subset=['emissions']).reset_index(drop=True)

    # Drop data before year 2000
    eu_emissions = eu_emissions[eu_emissions.year.astype(int) > 1999]

    # Convert the year column to datetime objects
    eu_emissions['year'] = pd.to_datetime(eu_emissions['year'], format='%Y')

    # Read in a file that maps EU sector names to US sector names
    sector_map = pd.read_csv('Pollution_Data/Sector_match.csv')

    # Create the mapping dict
    sector_map_dict = {}
    for row in range(len(sector_map.index)):
        sector_map_dict[sector_map.iloc[row, 0]] = sector_map.iloc[row, 1]

    # Map sector names via eu_emissions series
    eu_emissions.sector_name = eu_emissions.sector_name.map(sector_map_dict)

    # Drop sectors with no mapping (purposely leaving these sectors out of the analysis)
    eu_emissions = eu_emissions.dropna(subset=['sector_name']).reset_index(drop=True)

    return eu_emissions


def load_clean_us_emissions():
    """Function to load and cleanse the US data."""

    # Define the US emissions file name
    us_em_file = './Pollution_Data/us_emissions.csv'

    # Import the US emissions data file into a dataframe
    us_emissions = pd.read_csv(us_em_file)

    # Drop unnecessary columns
    us_emissions = us_emissions.drop(['STATE_FIPS', 'tier1_code'], axis=1)

    # Translate the columns into rows so there is one entry per year
    us_emissions_fix = pd.DataFrame()
    for col_num, col in enumerate(list(us_emissions.columns)):
        if 'emissions' in col:
            year_num = int(col[-2:])
            if year_num > 90:
                year = str(1900 + year_num)
            elif year_num < 20:
                year = str(2000 + year_num)
            else:
                continue

            tmp_df = us_emissions.iloc[:, 0:3]
            tmp_df['year'] = year
            tmp_df['emissions'] = us_emissions[col]
            us_emissions_fix = pd.concat([us_emissions_fix, tmp_df], ignore_index=True)

    us_emissions = us_emissions_fix

    # Convert column names to lower case
    us_emissions.columns = ['state', 'sector_name', 'pollutant_name', 'year', 'emissions']

    # Drop rows where the value is NaN
    us_emissions = us_emissions.dropna(subset=['emissions']).reset_index(drop=True)

    # Drop data before year 2000
    us_emissions = us_emissions[us_emissions.year.astype(int) > 1999]

    # Convert the year column to datetime objects
    us_emissions['year'] = pd.to_datetime(us_emissions['year'], format='%Y')

    # Fix the pollutant names to be consistent with EU data
    us_emissions.loc[us_emissions['pollutant_name'] == 'NOX', 'pollutant_name'] = 'NOx'
    us_emissions.loc[us_emissions['pollutant_name'] == 'PM25', 'pollutant_name'] = 'PM2.5'

    # Convert 1000 tons to Gg (to match EU reporting)
    us_emissions['emissions'] *= 0.907185

    return us_emissions


def define_pollutant_colors(us_df, eu_df):
    """Function to define a color dictionary for plot formatting for pollutants."""

    # First get a list of all the US and all the EU pollutants
    us_pollutants = list(us_df.pollutant_name.unique())
    eu_pollutants = list(eu_df.pollutant_name.unique())

    # Create one list without duplicates of the pollutant names
    pollutant_list = list(set(us_pollutants) | set(eu_pollutants))

    # Instantiate a categorical colormap
    colormap = plt.cm.tab10

    # Create a list of colors based on the number of pollutants
    colors = [colormap(i) for i in np.linspace(0, 0.9, len(pollutant_list))]

    # Create a dictionary to store the colors
    colordict = dict(zip(pollutant_list, colors))

    return colordict


def emissions_time_series(df, title=None, ylims=None, colordict=None):
    """Function to make a time series chart of emissions data."""

    # Define a lambda to normalize first value to 100
    scaler = lambda x: 100 * (x / x.iloc[0])

    # Compute sum of each pollutant each year across all states
    by_pollutant_year = df.groupby(['pollutant_name', 'year'], as_index=False).sum()

    # Transform the result to be scaled to 100
    by_pollutant_year['emissions'] = by_pollutant_year.groupby(
        'pollutant_name')['emissions'].transform(scaler)
    by_pollutant_year.set_index(['pollutant_name', 'year'], inplace=True)

    # Plot the results for all pollutants as a multi-line plot
    fig = plt.figure()
    for pollutant in by_pollutant_year.index.get_level_values(0).unique():
        plt.plot(by_pollutant_year.loc[pollutant]['emissions'],
                 label=pollutant, color=colordict[pollutant])
    plt.legend()
    plt.xlabel('Year')
    plt.ylabel(f'Total Emissions [% of {df.year.min().strftime("%Y")} Value]')
    if ylims is None:
        plt.ylim([0, 110])
    else:
        plt.ylim(ylims)
    if title is None:
        plt.title('Total US Emissions by Year')
    else:
        plt.title(title)
    plt.show()


def sector_time_series(df):
    """Function to create a time series heatmap of emissions data."""

    # Compute sum of each pollutant each year across all states
    by_pollutant_year = df.groupby(['pollutant_name', 'sector_name', 'year'], as_index=False).sum()

    # Narrow down to VOCs, sort by year, and convert years to strings
    by_pollutant_year = by_pollutant_year[by_pollutant_year.pollutant_name == 'VOC']
    by_pollutant_year = by_pollutant_year.sort_values('year')
    by_pollutant_year.year = by_pollutant_year.year.apply(lambda x: x.strftime('%Y'))

    # Create a pivoted dataframe for the heatmap
    pivoted = by_pollutant_year.pivot(index='sector_name', columns='year', values='emissions')
    
    # Create the heatmap figure
    fig, ax = plt.subplots(figsize=(8, 6)) 
    sns.heatmap(pivoted, ax=ax)
    plt.title('Emissions of SO2 in Gg from each sector from 2000 to 2017')
    plt.tight_layout()
    plt.ylabel('Sector')
    plt.xlabel('Year')
    plt.show()


def highest_sec(df):
    """This function takes in a dataframe and sorts sectors by highest emissions."""

    # Sort dataframe by values in emissions variable, return the top 5 as a series
    tmp_df = df.sort_values(['emissions'], ascending=False).head()
    return pd.Series(data=tmp_df.emissions.values, index=tmp_df.sector_name)


def define_sector_colors(us_df, eu_df):
    """Function to define a colormap for sectors for plotting."""

    # Create a list of US and EU sectors, sorted alphebetically
    us_sectors = sorted(list(us_df.sector_name.unique()))
    us_sectors = [re.sub(r'\W+', '', name).lower() for name in us_sectors]
    eu_sectors = sorted(list(eu_df.sector_name.unique()))
    eu_sectors = [re.sub(r'\W+', '', name).lower() for name in us_sectors]

    # Create a categorical colormap
    colormap = plt.cm.tab20

    # Create a list of colors for each sector
    colors = [colormap(i) for i in np.linspace(0, 0.9, len(us_sectors))]

    # Create separate colordicts for US and EU
    colordict_us = dict(zip(us_sectors, colors))
    colordict_eu = dict(zip(eu_sectors, colors))

    return colordict_us, colordict_eu


def emissions_sector_bars(df, tgt_year='2016', region='U.S.', colordict=None):
    """Function to create stacked bar charts for by-sector emissions."""

    # First we need to sum emissions across the entire region
    by_poll_year_sec = df.groupby(['pollutant_name', 'year', 'sector_name'], as_index=False)
    total_by_sector = by_poll_year_sec.sum()

    # Now we want to group by pollutant and year and apply the highest_sec function
    total_by_sector_grp = total_by_sector.groupby(['pollutant_name', 'year'])
    highest_sectors = total_by_sector_grp.apply(highest_sec)

    # Now let's pull out and plot the data for a specific year
    # Convert target year to a datetime object
    year_obj = datetime.strptime(tgt_year, '%Y')

    # We want to select only the data for a given year, which is the second level of the 3-level Multi-index
    pollutants = highest_sectors.index.get_level_values(0)
    sectors = highest_sectors.index.get_level_values(2)
    highest_sectors_tgt_year = highest_sectors.loc[(pollutants, year_obj, sectors)]

    # Define a categorical colormap
    test_df = highest_sectors_tgt_year.unstack()
    test_df = test_df.reindex(sorted(test_df.columns),  axis=1)
    try:
        colors = [colordict[re.sub(r'\W+', '', sector).lower()] for sector in test_df.columns]
    except:
        raise Exception("Provide a color dict")

    # Create stacked bar chart of the top 5 sectors for each pollutant, log scaled
    ax = test_df.plot(kind='bar', logy=True, stacked=True, color=colors, figsize=(10,6))

    # Define the x labels as the pollutant name
    ax.set_xticklabels(highest_sectors_tgt_year.index.get_level_values(0).unique())

    # Plot formatting and labels/title
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel('Pollutant')
    plt.ylabel('Emissions [Gg]')
    plt.title(f'Primary Contributing Sectors to {region}. Emissions in {tgt_year}')
    plt.tight_layout()
    plt.show()


def load_eu_locations():
    """Function to read in EU location data."""

    # Define the EU location file name
    eu_locations = './Pollution_Data/plotly_locations.csv'

    # Import the EU location data file into a dataframe
    eu_loc = pd.read_csv(eu_locations)
    
    return eu_loc


def load_us_locations():
    """Function to read in US location data."""

    # Define the US location file name
    us_locations = './Pollution_Data/plotly_locations_us.csv'

    # Import the US location data file into a dataframe
    us_loc = pd.read_csv(us_locations)      
    
    return us_loc


def load_pollutant_by_area(df, yr):
    """Function to transform and filter Particulate matter data."""    
    
    # Tranform and Filter PM Emissions by area
    PM_by_ctry = df.rename(columns={'state': 'subarea','country': 'subarea'})
    PM_by_ctry = PM_by_ctry.groupby(['subarea','year','pollutant_name']).emissions.sum().sort_values(ascending=False).unstack()
    PM_by_ctry = PM_by_ctry.filter(['PM2.5','PM10'])
    PM_by_ctry.reset_index(level=1, inplace=True)
    PM_by_ctry = PM_by_ctry.loc[(PM_by_ctry['year'].dt.year == yr)]

    return PM_by_ctry


def emissions_area_bars(df, pollutant, height, regions, clr):
    """Function to create horizontal bar charts for by-subarea emissions."""
    
    # Create horizontal bar chart for the subregions of EU and US respectively for the selected particulate matter
    fig = plt.figure(figsize = (20,height))
    ax = fig.add_subplot(1,1,1)
    df['PM' + pollutant].plot(kind='barh', color=clr)
    
    # Plot formatting and labels/title
    ax.set_ylabel('Emissions in Gg')
    ax.set_xlabel(regions)
    ax.set_title('Particulate Matter with diameter '+ pollutant +' microns or less')


def choro_table(df1,df2,pollutant):
    """Function to prepare data for choromap chart."""
    
    # Identify whether it is a EU or US dataset and merge with locations accordingly
    if 'country' in df1:
        df1 = df1.rename(columns={'country': 'subarea'})
        df1 = pd.merge(df1, df2, on='subarea')
        
    elif 'state' in df1:
        df1 = df1.rename(columns={'state': 'code'})
        df1 = pd.merge(df1, df2, on='code')
    
    # Transform and filter dataframe to prepare for chloropleth plotting
    df_pol_by_area = df1.groupby(['subarea','year','pollutant_name']).emissions.sum().sort_values(ascending=False).unstack()
    df_pol_by_area = df_pol_by_area.filter([pollutant])
    df_pol_by_area.reset_index(level=1, inplace=True)
    df_pol_by_area_2016 = df_pol_by_area.loc[(df_pol_by_area['year'].dt.year == 2016)]
    df_pol_by_area_2016 = pd.merge(df_pol_by_area_2016, df2, on='subarea')
    return df_pol_by_area_2016


def choro_table_norm(df1,pollutant):
    """Function to normalise pollutant data for choromap chart."""
    
    # Normalise dataframe pollution by population
    df1['norm']= df1[pollutant]*1000000/df1['population']
    return df1


def make_choropleth(df,pollutant,chloromap,is_norm, sc_max, sc_tick, map_type, loc_mode, us_norm):
    """Function to choromap emissions chart."""
    
    # Check whether it is normalised chart and adjust labels accordingly
    if is_norm == True:
        info = 'norm'
        sc_info = ' kg '
        title_info = ' (kg per capita)'

    else:
        info = pollutant
        sc_info = ' Gg '
        title_info = ' (total emissions)'
 
    if us_norm == True:
        chart_title = '2016 Particulate Matter ' + pollutant + title_info + ' - normalised relative to US'
    else:
        chart_title = '2016 Particulate Matter ' + pollutant + title_info
        
    # Create Choropleth
    data = [go.Choropleth(
        # Data source
        locations = df['code'],
        locationmode = loc_mode,
        z = df[info],
        text = df['subarea'],
        zauto = False, 
        zmax = sc_max, 
        zmin = 0, 
        
        # Adjust colourscale
        colorscale = [
            [0, "rgb(206, 48, 255)"],
            [0.1, "rgb(153, 0, 0)"],
            [0.2, "rgb(255, 0, 0)"],
            [0.3, "rgb(255, 100, 100)"],
            [0.4, "rgb(255, 154, 0)"],
            [0.5, "rgb(255, 207, 0)"],
            [0.6, "rgb(255, 255, 0)"],
            [0.7, "rgb(90, 120, 245)"],
            [0.8, "rgb(49, 207, 0)"],
            [0.9, "rgb(49, 255, 0)"],
            [1, "rgb(156, 255, 156)"]
        ],
        autocolorscale = False,
        reversescale = True,
        
        # Scale formatting
        marker = go.choropleth.Marker(
            line = go.choropleth.marker.Line(
                color = 'rgb(255,255,255)',
                width = 1
            )),
        colorbar = go.choropleth.ColorBar(
            ticksuffix = sc_info,
            dtick = sc_tick, 
            tick0 = 0, 
            tickmode = "linear", 
            title = pollutant),
        )]
    
    
    layout = go.Layout(
        # Title
        title = go.layout.Title(
            text = chart_title
        ),
        # Map display format
        geo = go.layout.Geo(
            showframe = False,
            showcoastlines = False,
            showlakes = True,
            lakecolor = 'rgb(255, 255, 255)',
            projection = go.layout.geo.Projection(type = map_type)
        )

    )
    # Plot chart
    fig = go.Figure(data = data, layout = layout)
    return py.iplot(fig, filename = chloromap)


def load_respiratory_mortality():
    """Function to load and seggregate respiratory mortality data."""
    
    # Italy and California respiratory mortality
    mortality = './health_Data/Italy_and_California.csv'

    # Import the EU location data file into a dataframe
    respiratory_mortality = pd.read_csv(mortality)

    # Convert the year column to datetime objects
    respiratory_mortality['Year'] = pd.to_datetime(respiratory_mortality['Year'], format='%Y')
    respiratory_mortality['Year'] = respiratory_mortality['Year'].dt.year
    respiratory_mortality = respiratory_mortality.rename(columns={'Year': 'year'})
    respiratory_mortality_ita = respiratory_mortality.filter(['year','Italy'])
    respiratory_mortality_cal = respiratory_mortality.filter(['year','California'])

    return respiratory_mortality_ita, respiratory_mortality_cal


def load_PM_dataframe_ita(eu_emissions, respiratory_mortality_ita):
    """Function to prepare data for Italy."""
    
    # Italy - Filter Particulate matter data and join with health data - respiratory related mortality
    italy_pm = eu_emissions.groupby(['country','year','pollutant_name']).emissions.sum().sort_values(ascending=False).unstack()
    italy_pm = italy_pm.filter(['PM2.5','PM10', 'NOx'])
    italy_pm.reset_index(level=1, inplace=True)
    italy_pm = italy_pm.groupby(['country']).get_group('Italy')
    italy_pm['year'] = italy_pm['year'].dt.year
    italy_pm = pd.merge(italy_pm, respiratory_mortality_ita, on='year')
    italy_pm = italy_pm.rename(columns={'subarea': 'state','Italy': 'Mortality'})
    
    return italy_pm


def load_PM_dataframe_cal(us_emissions, respiratory_mortality_cal, us_loc):
    """Function to prepare data for Italy."""
    
    # California - Filter Particulate matter data and join with health data - respiratory related mortality
    california_pm = us_emissions.rename(columns={'state': 'code'})
    california_pm = california_pm.groupby(['code','year','pollutant_name']).emissions.sum().sort_values(ascending=False).unstack()
    california_pm.reset_index(level=1, inplace=True)
    california_pm = pd.merge(california_pm, us_loc, on='code')
    california_pm = california_pm.groupby(['subarea']).get_group('California')
    california_pm = california_pm.filter(['year','subarea','PM2.5','PM10','NOx'])
    california_pm['year'] = california_pm['year'].dt.year
    california_pm = pd.merge(california_pm, respiratory_mortality_cal, on='year')
    california_pm = california_pm.rename(columns={'subarea': 'state','California': 'Mortality'})
    
    return california_pm


def mortality_vs_particulate_matter(df, country):
    """Function to create combined chart for Particulate matter emissions and mortality rates."""
    
    fig = plt.figure(figsize = (20,5))
    ax = fig.add_subplot(1,1,1)
    ax2 = ax.twinx()
    width = 0.25   

    df['PM2.5'].plot(kind='bar', color='#7293CB', ax=ax, width=width, position=1)
    df['PM10'].plot(kind='bar', color='#84BA5B', ax=ax, width=width, position=0)
    df['Mortality'].plot(color='red', ax=ax2, linestyle='-', marker='o', linewidth=2.0)

    ax.set_ylabel('Particulate matter emissions in Gg')
    ax2.set_ylabel('Number of deaths')
    ax.set_xlabel('Year')

    ax.set_title(country + ' Respiratory problem related deaths and Particulate Matter emissions')
    ax.set_xticklabels(df['year'], rotation = 90)

    ax.set_yticks([100,200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400])
    ax2.set_yticks([0,10000,20000,30000,40000,50000])

    ax.legend(bbox_to_anchor = (0.07, 0.99))
    ax2.legend(bbox_to_anchor = (0.083, 0.85))


if __name__ == "__main__":

    ### Load and Clean EU Emissions
    eu_emissions = load_clean_eu_emissions()

    ### Load and Clean US Emissions
    us_emissions = load_clean_us_emissions()

    ### Question: How has US and EU pollution changed from 1996-2016?    
    colordict = define_pollutant_colors(us_emissions, eu_emissions)
    emissions_time_series(us_emissions, ylims=[0, 120], colordict=colordict)
    emissions_time_series(eu_emissions, ylims=[0, 120], title='Total EU Emissions by Year', colordict=colordict)

    sector_time_series(us_emissions)

    ### Question: Which sectors are the biggest contributors to pollution in 2016?
    colordict_us, colordict_eu = define_sector_colors(us_emissions, eu_emissions)
    emissions_sector_bars(us_emissions, tgt_year='2016', region='U.S.', colordict=colordict_us)
    emissions_sector_bars(eu_emissions, tgt_year='2016', region='EU', colordict=colordict_eu)

    ## Question: What states in the US have the highest emissions of PM2.5 in 2016?
    ## What about the lowest?

    # us_PM25_2016_by_state = us_emissions_mm.groupby(
    #     'year').get_group('2016').groupby(['pollutant_name','state']).sum().unstack().T
    # us_PM25_2016_by_state /= us_PM25_2016_by_state.max()
    # ax = sns.heatmap(us_PM25_2016_by_state.iloc[:26], xticklabels=True, yticklabels=True)
    # plt.ylabel('State')
    # plt.xlabel('Pollutant')
    # plt.tight_layout()
    # plt.show()
