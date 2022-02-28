from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

from Consumption import Retrospective
from MetaData import Characteristics
import numpy as np
from math import exp

# Fetch buildings characteristics
metadata = Characteristics()
meta_df = metadata.metadata_df


def consumptionByCategoricalCharacteristic(characteristic, start_time=datetime(2019, 1, 1, 0),
                                           end_time=datetime(2020, 1, 1, 0),
                                           nbOfBuildingByCharacteristic=2, characteristicRange=6):
    characteristic_list = meta_df[characteristic].value_counts(dropna=False)[
                          0:characteristicRange].index.tolist()

    # Missing values
    missingValidPropertyDataByCharacteristic = {characteristic: characteristic_list,
                                                'Missing Data': [0 for i in range(characteristicRange)],
                                                'Valid Data': [0 for i in range(characteristicRange)]}

    # To find the buildings' id for each different characteristic
    idsByCharac = pd.DataFrame(columns=[characteristic, "property_id", "average_heat", "average_electricity"])

    for charElement in characteristic_list:
        charDF = meta_df.loc[(meta_df[characteristic] == charElement)][0:nbOfBuildingByCharacteristic]
        ids = charDF["property_id"].tolist()

        retro = Retrospective(ids, start_time, end_time)
        for building_id in ids:
            mean = retro.getMeanEnergyByProperty(building_id)

            characteristic_index = missingValidPropertyDataByCharacteristic[characteristic].index(charElement)
            if mean[0] != mean[0] or mean[1] != mean[1]:
                missingValidPropertyDataByCharacteristic['Missing Data'][characteristic_index] += 1
                mean[0] = 0
                mean[1] = 0
            else:
                missingValidPropertyDataByCharacteristic['Valid Data'][characteristic_index] += 1
                mean[0] = round(mean[0], 2)
                mean[1] = round(mean[1], 2)

                dic = {characteristic: charElement,
                       "property_id": building_id,
                       "average_heat": mean[0],
                       "average_electricity": mean[1]}

                idsByCharac = idsByCharac.append(dic, ignore_index=True)

    # General means by use
    meanByCharacteristicDF = idsByCharac.groupby(characteristic).mean()
    meanByCharacteristicDF = meanByCharacteristicDF.reset_index()

    print(meanByCharacteristicDF)

    # ---------------------------- Graphs --------------------------
    # To plot the number of missing/invalid vs valid values-------------------------

    missingValidDataDF = pd.DataFrame.from_dict(missingValidPropertyDataByCharacteristic)
    missingValidDataDF = missingValidDataDF.set_index(characteristic)
    meanByCharacteristicDF = meanByCharacteristicDF.drop("property_id", axis=1, errors="ignore")

    print(missingValidDataDF)

    Ntotal = missingValidDataDF["Valid Data"].sum() + missingValidDataDF["Missing Data"].sum()

    fig = missingValidDataDF[['Missing Data', 'Valid Data']].plot(stacked=True,
                                                                  width=0.7,
                                                                  figsize=(12, 6),
                                                                  kind='bar',
                                                                  xlabel=characteristic,
                                                                  ylabel="Total Number of Buildings sample",
                                                                  rot=0,
                                                                  color=["dodgerblue", "lightgray"],
                                                                  fontsize="large",
                                                                  )
    plt.title("Number of Missing/Invalid & Valid Building samples by " + characteristic + ", N=" + str(
        Ntotal) + "(N: total number of samples)", fontweight="bold",
              fontsize=16)

    fig = fig.get_figure()
    fig.savefig('../Graphs/CategoricalCharacteristic/' + characteristic + '/' + characteristic + 'MissingData.png')

    # plt.show()

    # To plot the Proportion of missing/invalid vs valid values-------------------------

    missingValidDataDF_prop = pd.DataFrame(columns=[characteristic, 'Missing Data', 'Valid Data'])
    for char_elem in missingValidDataDF.index.tolist():
        missing_data = missingValidDataDF.loc[char_elem, 'Missing Data']
        valid_data = missingValidDataDF.loc[char_elem, 'Valid Data']

        missing_prop = round((missing_data / (missing_data + valid_data)), 2)
        valid_data = round((valid_data / (missing_data + valid_data)), 2)

        dic = {characteristic: char_elem,
               'Missing Data': missing_prop,
               'Valid Data': valid_data}

        missingValidDataDF_prop = missingValidDataDF_prop.append(dic, ignore_index=True)

    missingValidDataDF_prop = missingValidDataDF_prop.set_index(characteristic)

    fig = missingValidDataDF_prop[['Missing Data', 'Valid Data']].plot(stacked=True,
                                                                       width=0.7,
                                                                       figsize=(14, 6),
                                                                       kind='bar',
                                                                       xlabel=characteristic,
                                                                       ylabel="Proportion of missing or valid Buildings sample ",
                                                                       rot=0,
                                                                       color=["dodgerblue", "lightgray"],
                                                                       fontsize="large",
                                                                       )
    plt.title("Proportion of Missing/Invalid & Valid Building samples by " + characteristic + ", N=" + str(Ntotal),
              fontweight="bold",
              fontsize=16)

    for n, x in enumerate([*missingValidDataDF.index.values]):

        for (proportion, count, y_loc) in zip(missingValidDataDF_prop.loc[x],
                                              missingValidDataDF.loc[x],
                                              missingValidDataDF_prop.loc[x].cumsum()):
            if proportion > 0:
                plt.text(x=n - 0.17,
                         y=(y_loc - proportion) + (proportion / 2),
                         s=f'{count}\n({np.round(proportion * 100, 1)}%)',
                         color="black",
                         fontsize=12,
                         fontweight="bold")

    fig = fig.get_figure()
    fig.savefig(
        '../Graphs/CategoricalCharacteristic/' + characteristic + '/ ' + characteristic + 'ProportionMissingData.png')

    # To plot the average energy consumption of by characteristic-------------------------

    Nvalid = missingValidDataDF["Valid Data"].sum()

    fig = meanByCharacteristicDF.plot.bar(x=characteristic,
                                          rot=0,
                                          width=0.8,
                                          color=["darkorange", "royalblue"],
                                          figsize=(10, 4),
                                          xlabel=characteristic,
                                          ylabel="Average Energy Consumption",
                                          fontsize='large')

    plt.title('Average Energy Consumption by ' + characteristic + ', N=' + str(Nvalid)
              + "(N: number of valid samples)", fontweight="bold", fontsize=16)

    fig = fig.get_figure()
    fig.savefig(
        '../Graphs/CategoricalCharacteristic/' + characteristic + '/averageConsumptionBy' + characteristic + '.png')


def consumptionByContinuousCharacteristic(characteristic, start_time=datetime(2019, 1, 1, 0),
                                          end_time=datetime(2020, 1, 1, 0),
                                          nbOfBuildingByCharacteristic=5, distribution_range=6):
    # To create a dataframe to list and logarithmically distribute a continuous characteristics
    characteristic_df = pd.DataFrame()
    characteristic_df["property_id"] = meta_df["property_id"]
    characteristic_df[characteristic] = meta_df[characteristic]
    characteristic_df = characteristic_df[characteristic_df[characteristic] > 0.0]
    characteristic_df["log " + characteristic] = np.log(meta_df[characteristic])
    characteristic_df = characteristic_df.sort_values(by="log " + characteristic)

    log_min = min(characteristic_df["log " + characteristic])
    log_max = max(characteristic_df["log " + characteristic])

    # To create interval list of continuous characteristic
    gap = log_max - log_min
    distrib_factor = gap / distribution_range
    distrib_list = [log_min + i * distrib_factor for i in range(distribution_range + 1)]

    # logarithmic distribution
    distrib_interval_list = []
    # reconverted and rounded gross distribution of characteristics
    gross_distrib_interval_list = []
    for i in range(len(distrib_list) - 1):
        distrib_interval_list.append((distrib_list[i], distrib_list[i + 1]))
        gross_distrib_interval_list.append((round(exp(distrib_list[i]), 2), round(exp(distrib_list[i + 1]), 2)))

    # Missing values
    missingValidPropertyDataByCharacteristic = {characteristic: gross_distrib_interval_list,
                                                'Missing Data': [0 for i in range(distribution_range)],
                                                'Valid Data': [0 for i in range(distribution_range)]}

    # To find the buildings' id for each different characteristic
    idsByCharac = pd.DataFrame(columns=[characteristic, "property_id", "average_heat", "average_electricity"])

    for i in range(distribution_range):

        in_class_characteristic = (characteristic_df["log " + characteristic] >= distrib_interval_list[i][0]) & (
                characteristic_df["log " + characteristic] < distrib_interval_list[i][1])

        charDF = characteristic_df.loc[in_class_characteristic][0:nbOfBuildingByCharacteristic]
        ids = charDF["property_id"].tolist()

        retro = Retrospective(ids, start_time, end_time)
        for building_id in ids:
            mean = retro.getMeanEnergyByProperty(building_id)

            characteristic_index = missingValidPropertyDataByCharacteristic[characteristic].index(
                gross_distrib_interval_list[i])
            if mean[0] != mean[0] or mean[1] != mean[1]:
                missingValidPropertyDataByCharacteristic['Missing Data'][characteristic_index] += 1
                mean[0] = 0
                mean[1] = 0
            else:
                missingValidPropertyDataByCharacteristic['Valid Data'][characteristic_index] += 1
                mean[0] = round(mean[0], 2)
                mean[1] = round(mean[1], 2)

                dic = {characteristic: gross_distrib_interval_list[characteristic_index],
                       "property_id": building_id,
                       "average_heat": mean[0],
                       "average_electricity": mean[1]}

                idsByCharac = idsByCharac.append(dic, ignore_index=True)

    # General means by use
    meanByCharacteristicDF = idsByCharac.groupby(characteristic).mean()
    meanByCharacteristicDF = meanByCharacteristicDF.reset_index()
    meanByCharacteristicDF = meanByCharacteristicDF.set_index(characteristic)

    # -----------------------Graphs-----------------------------
    # To plot the number of missing/invalid vs valid values-------------------------

    missingValidDataDF = pd.DataFrame.from_dict(missingValidPropertyDataByCharacteristic)
    missingValidDataDF = missingValidDataDF.set_index(characteristic)
    meanByCharacteristicDF = meanByCharacteristicDF.drop("property_id", axis=1, errors="ignore")

    Ntotal = missingValidDataDF["Valid Data"].sum() + missingValidDataDF["Missing Data"].sum()

    fig = missingValidDataDF[['Missing Data', 'Valid Data']].plot(stacked=True,
                                                                  width=0.7,
                                                                  figsize=(12, 6),
                                                                  kind='bar',
                                                                  xlabel=characteristic,
                                                                  ylabel="Total Number of Buildings sample",
                                                                  rot=0,
                                                                  color=["dodgerblue", "lightgray"],
                                                                  fontsize="large",
                                                                  )
    plt.title("Number of Missing/Invalid & Valid Building samples by " + characteristic + ", N=" + str(
        Ntotal) + "(N: total number of samples)", fontweight="bold",
              fontsize=16)

    fig = fig.get_figure()
    fig.savefig('../Graphs/ContinuousCharacteristic/' + characteristic + '/' + characteristic + 'MissingData.png')

    # To plot the average energy consumption of by characteristic-------------------------

    Nvalid = missingValidDataDF["Valid Data"].sum()

    fig = meanByCharacteristicDF.plot.bar(rot=0,
                                          width=0.8,
                                          color=["darkorange", "royalblue"],
                                          figsize=(10, 4),
                                          xlabel=characteristic,
                                          ylabel="Average Energy Consumption",
                                          fontsize='large')

    plt.title('Average Energy Consumption by ' + characteristic + ', N=' + str(Nvalid)
              + "(N: number of valid samples)", fontweight="bold", fontsize=16)

    fig = fig.get_figure()
    fig.savefig(
        '../Graphs/ContinuousCharacteristic/' + characteristic + '/averageConsumptionBy' + characteristic + '.png')


# ---------
"""categoricalCharacteristics = ["intended_use", "district_name", "year_built", "floorcount", "postal_code"]

for char in categoricalCharacteristics:
    print("Starting................")
    print(char)

    nbOfBuildingByCharacteristic = 30
    characteristicRange = 6
    if char == "floorcount":
        characteristicRange = 6

    consumptionByCategoricalCharacteristic(char, nbOfBuildingByCharacteristic=nbOfBuildingByCharacteristic,
                                           characteristicRange=characteristicRange)

    print("Done................")"""

# -----------
continuousCharacteristics = ["volume", "grossarea", "year_built", "year_renovated"]

for char in continuousCharacteristics:
    print("Starting................")
    print(char)

    nbOfBuildingByCharacteristic = 30
    distribution_range = 6

    consumptionByContinuousCharacteristic(char, nbOfBuildingByCharacteristic=nbOfBuildingByCharacteristic,
                                          distribution_range=distribution_range)
    print("Done................")
