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
            print("Downloading the metadata...")
            bas_df = pd.read_csv('../Data/ids_properties.csv')

            # To remove buildings without records
            forbiden_df = bas_df[bas_df['property_id'].isin(forbiden_ids)]
            bas_df = bas_df.drop(forbiden_df.index)

            # Translate intended uses
            translateIntendedUse(bas_df)

            # Change most recorded intended uses
            useDict = {"511 Buildings for educational institutions": "Educational buildings",
                       "231 Kindergartens": "Kindergartens",
                       "214 Health Centers": "Health Centers",
                       "359 Other sports and fitness buildings": "Sports and fitness buildings",
                       "221 Retirement homes": "Retirement homes",
                       "151 Office buildings": "Offices",
                       "229 Other service plant buildings": "Plant buildings",
                       "721 Fire stations": "Fire stations",
                       "322 Libraries and archives": "Libraries",
                       "719 Other storage buildings": "Storage buildings"}
            for use in useDict.keys():
                bas_df.loc[(bas_df.intended_use == use), 'intended_use'] = useDict[use]

            # Reseting indexes
            bas_df = bas_df.reset_index(drop=True)

            self.metadata_df = bas_df

            # Download df to a pkl file
            self.metadata_df.to_pickle("../Data/translated_metadata.pkl")

        else:
            print("The metadata is already downloaded")
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
