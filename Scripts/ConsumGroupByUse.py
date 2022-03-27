from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

from Consumption import Retrospective
from MetaData import Characteristics
import numpy as np
from math import exp

# Initializing metadata
c = Characteristics()
meta_df = c.metadata_df

def consumptionByCharacGroupByUse(characteristic,
                                  start_time=datetime(2016, 1, 1, 0),
                                  end_time=datetime(2020, 1, 1, 0),
                                  nbOfBuildingByCharacteristic=10,
                                  distribution_range=4):
    # To create a dataframe to list and logarithmically distribute a continuous characteristics
    characteristic_df = pd.DataFrame()

    useList = meta_df["intended_use"].value_counts().index.to_list()
    selectedUses = useList[0:3]

    characteristic_df["property_id"] = meta_df[meta_df["intended_use"].isin(selectedUses)]["property_id"]
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
    idsByCharac = pd.DataFrame(
        columns=[characteristic, "property_id", "intended_use", "average_heat", "average_electricity"])

    for i in range(distribution_range):
        #
        in_class_characteristic = (characteristic_df["log " + characteristic] >= distrib_interval_list[i][0]) & (
                characteristic_df["log " + characteristic] < distrib_interval_list[i][1])

        charDF = characteristic_df.loc[in_class_characteristic][0:nbOfBuildingByCharacteristic]

        ids = charDF["property_id"].tolist()
        retro = Retrospective(ids, start_time, end_time)

        for building_id in ids:
            mean = retro.getMeanEnergyByProperty(building_id)

            # Counting invalid data
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

                # if the data is valid, add it to results
                use = meta_df[meta_df["property_id"] == building_id]["intended_use"].value_counts().index.to_list()[0]

                dic = {characteristic: gross_distrib_interval_list[characteristic_index],
                       "property_id": building_id,
                       "intended_use": use,
                       "average_heat": mean[0],
                       "average_electricity": mean[1]}

                idsByCharac = idsByCharac.append(dic, ignore_index=True)

    # General means by use
    meanByCharacteristicDF = idsByCharac.groupby(characteristic).mean()
    meanByCharacteristicDF = meanByCharacteristicDF.reset_index()
    meanByCharacteristicDF = meanByCharacteristicDF.set_index(characteristic)

    col = [characteristic + " range"]
    for use in selectedUses:
        col.append(use + " avg consumption")

    meanByVolumeGroupByUseDF = pd.DataFrame(columns=col)
    meanByVolumeGroupByUseDF[characteristic + " range"] = gross_distrib_interval_list

    heatMeanByVolumeGroupByUseDF = meanByVolumeGroupByUseDF.copy()
    elecMeanByVolumeGroupByUseDF = meanByVolumeGroupByUseDF.copy()

    for use in selectedUses:
        useDF = idsByCharac[idsByCharac["intended_use"] == use][["volume", "average_heat", "average_electricity"]]

    heatUseConsumList = []
    elecUseConsumList = []

    for volume_range in gross_distrib_interval_list:
        heatAvg = useDF[useDF["volume"] == volume_range]["average_heat"].mean()
        elecAvg = useDF[useDF["volume"] == volume_range]["average_electricity"].mean()

        heatUseConsumList.append(heatAvg)
        elecUseConsumList.append(elecAvg)

    heatMeanByVolumeGroupByUseDF[use + " avg consumption"] = heatUseConsumList
    elecMeanByVolumeGroupByUseDF[use + " avg consumption"] = elecUseConsumList

    # Plotting ------------------------------------------
    # Heat
    fig = heatMeanByVolumeGroupByUseDF.plot.bar(
        title='Heat Consumption By ' + characteristic + " and Group By Intended Use",
        x=characteristic + " range",
        rot=0,
        width=0.8,
        color=['yellowgreen', 'tomato', 'skyblue'],
        figsize=(12, 6),
        xlabel=characteristic + " range",
        ylabel="Average Heat Consumption",
        fontsize='large',
    )
    fig = fig.get_figure()
    fig.savefig('../Graphs/ConsumGroupByUse/heatConsumGroupByUse')

    # Elec
    fig = elecMeanByVolumeGroupByUseDF.plot.bar(
        title='Electricity Consumption By ' + characteristic + " and Group By Intended Use",
        x=characteristic + " range",
        rot=0,
        width=0.8,
        color=['yellowgreen', 'tomato', 'skyblue'],
        figsize=(12, 6),
        xlabel=characteristic + " range",
        ylabel="Average Electricity Consumption",
        fontsize='large'
    )
    fig = fig.get_figure()
    fig.savefig('../Graphs/ConsumGroupByUse/elecConsumGroupByUse')


# Initializing parameters
start_time = datetime(2016, 1, 1, 0)
end_time = datetime(2020, 1, 1, 0)

nbOfBuildingByCharacteristic = 100
distribution_range = 4

characteristic = "volume"

consumptionByCharacGroupByUse(characteristic=characteristic)