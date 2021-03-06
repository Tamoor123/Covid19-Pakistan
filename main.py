import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import plotly.graph_objects as go
import os

# loading data-sets
df_confirmed = pd.read_csv("dataset/time_series_covid19_confirmed_global.csv")
df_deaths = pd.read_csv("dataset/time_series_covid19_deaths_global.csv")
df_recovered = pd.read_csv("dataset/time_series_covid19_recovered_global.csv")

do_plot = False

# Data exploration
df_confirmed.head()
df_deaths.head()
df_recovered.head()

print(df_confirmed.shape)
print(df_deaths.shape)
print(df_recovered.shape)

# I'm mostly interested in Pakistan's  data so I'll focus on that.
df_pak_confirmed = df_confirmed[df_confirmed["Country/Region"] == "Pakistan"]
df_pak_deaths = df_deaths[df_deaths["Country/Region"] == "Pakistan"]
df_pak_recovered = df_recovered[df_recovered["Country/Region"] == "Pakistan"]

# Let's drop Latitude, Longitude and State as they don't provide any useful information
df_pak_confirmed = df_pak_confirmed.drop(['Country/Region', 'Province/State', 'Lat', "Long"], axis=1)
df_pak_deaths = df_pak_deaths.drop(['Country/Region', 'Province/State', 'Lat', "Long"], axis=1)
df_pak_recovered = df_pak_recovered.drop(['Country/Region', 'Province/State', 'Lat', "Long"], axis=1)

# Transpose for better visualization
df_pak_confirmed = df_pak_confirmed.T.reset_index()
col_confirmed = ["Date", "Cases"]
df_pak_confirmed.columns = col_confirmed

df_pak_deaths = df_pak_deaths.T.reset_index()
col_deaths = ["Date", "Deaths"]
df_pak_deaths.columns = col_deaths

df_pak_recovered = df_pak_recovered.T.reset_index()
col_recovered = ["Date", "Recovered"]
df_pak_recovered.columns = col_recovered

print(df_pak_confirmed.shape)
print(df_pak_deaths.shape)
print(df_pak_recovered.shape)

# merging into a single data frame
df_pakistan = df_pak_confirmed
df_pakistan["Deaths"] = df_pak_deaths['Deaths']
df_pakistan["Recovered"] = df_pak_recovered['Recovered']
df_pakistan['ActiveCases'] = df_pakistan['Cases'] - (df_pakistan['Deaths'] + df_pakistan['Recovered'])

df_pakistan['Date'] = pd.to_datetime(df_pakistan["Date"], infer_datetime_format=True)

# combining data for every other country except Pakistan
df_world = df_confirmed[df_confirmed['Country/Region'] != "Pakistan"]
df_world = df_world.drop(['Province/State', 'Lat', "Long"], axis=1)
df_world = df_world.groupby(["Country/Region"]).sum()  # add cases for different states of same country to get a total

# Transpose to get time series
df_world = df_world.T.reset_index()

df_world.rename(columns={"index": "Date"}, inplace=True)

df_world['Date'] = pd.to_datetime(df_world["Date"], infer_datetime_format=True)

top_countries = ["Date", "Iran", "France", "China", "US", "United Kingdom"]

df_top = df_world[top_countries]  # selecting only countries with highest cases


# initial visualization
def plot_comparison():
    fig, ax = plt.subplots()
    ax.set_yscale('log')
    ax.plot(df_pakistan['Date'], df_pakistan['Cases'], label="Pakistan")
    ax.plot(df_top['Date'], df_top['China'], label="China")
    ax.plot(df_top['Date'], df_top['US'], label="US")
    ax.plot(df_top['Date'], df_top['Iran'], label="Iran")
    ax.plot(df_top['Date'], df_top['France'], label="France")
    ax.set(xlabel="Date",
           ylabel="Confirmed Cases",
           title="Covid-19 Cases")
    ax.legend()
    date_form = DateFormatter("%d-%m")
    ax.xaxis.set_major_formatter(date_form)

    plt.show()


if do_plot:
    plot_comparison()

if not os.path.exists("images"):
    os.mkdir("images")


def plot_zero_day_progression(scale="linear"):
    df_zero_day_iran = df_top["Iran"]
    df_zero_day_iran = df_zero_day_iran[df_zero_day_iran > 0].values

    df_zero_day_pakistan = df_pakistan['Cases']
    df_zero_day_pakistan = df_zero_day_pakistan[df_zero_day_pakistan > 0].values

    df_zero_day_US = df_top["US"]
    df_zero_day_US = df_zero_day_US[df_zero_day_US > 0].values

    df_zero_day_UK = df_top["United Kingdom"]
    df_zero_day_UK = df_zero_day_UK[df_zero_day_UK > 0].values

    fig, ax = plt.subplots()
    ax.plot(df_zero_day_pakistan, label="Pakistan")
    ax.plot(df_zero_day_iran, label="Iran")
    ax.plot(df_zero_day_UK, label="UK")
    ax.plot(df_zero_day_US, label="US")
    ax.set(xlabel="No of days since the first case",
           ylabel="Confirmed Cases",
           title="Covid-19 Cases " + scale + " scale")
    ax.set_yscale(scale)
    ax.legend()
    plt.show()
    plt.savefig("images/zeroday_prog_"+scale+".png")


def plot_daily_change_pakistan():
    diff_pk = df_pakistan['Cases'].diff().fillna(0)

    df_pakistan['DailyChange'] = diff_pk

    data = go.Bar(
        x=df_pakistan['Date'],
        y=df_pakistan['DailyChange'],
        name="Daily Change",

    )

    fig = go.Figure(data=data)
    # fig.show()

    fig.write_image("images/DailyChangePakistan.png")


if do_plot:
    plot_daily_change_pakistan()
    plot_zero_day_progression()
    plot_zero_day_progression(scale="log")




