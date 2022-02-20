import pandas as pd
from deep_translator import GoogleTranslator
from os.path import exists
import csv

with open('../Data/forbiden_ids.csv', newline='') as f:
    reader = csv.reader(f)
    forbiden_ids = list(reader)[2]
forbiden_ids=list(map(float, forbiden_ids))


class Characteristics():
    def __init__(self):
        if not exists("../Data/translated_metadata.pkl"):
            bas_df = pd.read_csv('ids_properties.csv')

            # To remove buildings without records
            forbiden_df = bas_df[bas_df['property_id'].isin(forbiden_ids)]
            bas_df = bas_df.drop(forbiden_df.index)

            # Translate intended uses
            translateIntendedUse(bas_df)

            # Reseting indexes
            bas_df = bas_df.reset_index(drop=True)

            self.metadata_df = bas_df

            # Download df to a pkl file
            self.metadata_df.to_pickle("../Data/translated_metadata.pkl")

        else:
            print("It exists")
            self.metadata_df = pd.read_pickle("../Data/translated_metadata.pkl")


def translateIntendedUse(df):
    # Saving the intended uses
    useDf = df["intended_use"].values.tolist()

    # Translating the sub-dataframe
    new_use_list = []
    i = 0
    for use in useDf:
        if isinstance(use, str):
            new_use_list.append(GoogleTranslator(source='fi', target='en').translate(text=use))
        else:
            new_use_list.append("Error")

    # Deleting obsolete columns
    df.drop("intended_use", axis=1, inplace=True)

    # Putting the new normalized column to the df
    df["intended_use"] = new_use_list
