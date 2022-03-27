from Consumption import *
from MetaData import *
import matplotlib.pyplot as plt
import os


def getMeanDF(retrospective, id_list):
    """
    Returns the basic meta df concatanated with the average consumption of each property
    """

    heat_means = []
    elec_means = []
    for prop_id in id_list:
        mean = retrospective.getMeanEnergyByProperty(prop_id)
        heat_means.append(mean[0])
        elec_means.append(mean[1])
        print(str(mean[0]) + ", " + str(mean[1]))

    new_meta_df = meta_df[meta_df['property_id'].isin(id_list)]
    new_meta_df["heat_mean"] = heat_means
    new_meta_df["elec_mean"] = elec_means

    return new_meta_df


# Retrieving metadata
c = Characteristics()
meta_df = c.metadata_df

# Setting time parameters
start_time = datetime(2015, 1, 1, 0)
end_time = datetime(2020, 1, 1, 0)

# Getting the most recorded intended uses
use_list = meta_df["intended_use"].value_counts()[0:5].index.to_list()
print(use_list)

# Create directory if it doesn't exist
dirName = '../Graphs/useConsumption/'
try:
    # Create target Directory
    os.mkdir(dirName)
    print("Directory ", dirName, " Created ")
except FileExistsError:
    print("Directory ", dirName, " already exists")

for use in use_list:
    print(use)
    # Setting metadata dataframe from a particular intended use
    uses_df = meta_df[meta_df["intended_use"] == use]
    id_list = uses_df["property_id"][0:100]


    # Setting a retrospective object
    print("Processing " + use + " retrospective....")
    r = Retrospective(id_list, start_time, end_time)
    cons_df = r.consumption_df
    print("Processing done")
    print("")

    new_meta_df = getMeanDF(r, id_list)

    # Graphs
    fig, axes = plt.subplots(1, 2)

    new_meta_df[new_meta_df["intended_use"] == use].plot(
        ax=axes[0],
        kind='scatter',
        x='grossarea',
        y='volume',
        c='elec_mean',
        colormap='cividis',
        label=use,
        figsize=(14, 6));

    new_meta_df[new_meta_df["intended_use"] == use].plot(
        ax=axes[1],
        kind='scatter',
        x='grossarea',
        y='volume',
        c='heat_mean',
        colormap='cividis',
        label=use,
        figsize=(14, 6));
    fig.suptitle("Consumption average of " + use + ", by gross area and volume", fontsize=10)
    fig = fig.get_figure()

    plt.savefig("../Graphs/useConsumption/" + use + ".png")

