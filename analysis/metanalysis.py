import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# csvs from ALB, BOS, JFK and PVD
PROJECT_ROOT = Path(__file__).resolve().parents[1]
csv_files = sorted((PROJECT_ROOT / "data" / "processed").glob("*_hourly_2024_cleaned.csv"))
print(csv_files)

dfs ={}

for file in csv_files:
    # read the csv file into a dataframe
    df = pd.read_csv(file)
    # convert the "DATE" column to datetime format
    df['DATE'] = pd.to_datetime(df['DATE'])
    # store the dataframe in the dictionary with the station name as the key
    dfs[file.stem.split('_')[0]] = df

# extract only the 54th minute for BOS, and 51th minute for ALB, JFK, and PVD
minute_offsets = {
    "bos": 54,
    "alb": 51,
    "jfk": 51,
    "pvd": 51,
}


# dataframes = [pd.read_csv(file) for file in csv_files]

# print(csv_files)
# print(len(dfs))

# for df in dfs.values():
#     # convert the "DATE" column to datetime format for each dataframe
#     df['DATE'] = pd.to_datetime(df['DATE'])
#     # print dtypes of each dataframe
#     print(df.dtypes)
#     print(df.head())

# plot January "HourlyDryBulbTemperature" for each station
# plot January "daily precipitation" by adding each hourly precipitation for each station

fig, ax1 = plt.subplots(figsize=(12, 6))

ax2 = ax1.twinx()  # create secondary y-axis once

for station, df in dfs.items():
    minute_offset = minute_offsets[station]
    
    hourly_df = df[df["DATE"].dt.minute == minute_offset]
    jan_df = hourly_df[hourly_df["DATE"].dt.month == 1].copy()
    jan_df = jan_df.sort_values("DATE")
    
    ax1.plot(
        jan_df["DATE"],
        jan_df["HourlyDryBulbTemperature"],
        label=f"{station} Temperature"
    )
    
    daily_precip = (jan_df.assign(date=jan_df["DATE"].dt.date).groupby("date", as_index=False)["HourlyPrecipitation"].sum())
    
    ax2.bar(
        daily_precip["date"],
        daily_precip["HourlyPrecipitation"],
        label=f"{station} Daily Precipitation",
        alpha=0.3,
        width=0.2
    )

ax1.set_xlabel("Date")
ax1.set_ylabel("Hourly Dry Bulb Temperature")
ax2.set_ylabel("Hourly Precipitation")

plt.title("January Hourly Dry Bulb Temperature and Precipitation for Each Station")

# combine legends from both axes
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

#plt.show()




# distribution
# correlation


#print(dfs)

bos_df = dfs['bos']
hourly_bos_df = bos_df[bos_df["DATE"].dt.minute == 54]
hourly_bos_df = hourly_bos_df[hourly_bos_df["DATE"].dt.month <= 3].copy()


plt.figure()
plt.hist(hourly_bos_df['HourlyDryBulbTemperature'], color='b', bins=50)
plt.show()
