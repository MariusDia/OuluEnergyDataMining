from datetime import datetime
from itertools import product
import pandas as pd

hourly_url = "https://api.ouka.fi/v1/properties_consumption_hourly"


class Retrospective():
    def __init__(self, property_ids, start_time, end_time, dropna=False):
        """
        Create a dataframe containing the energy consumption of properties
        listed by their ids during a precise time interval.
        We can also choose to retrieve only a certain energy type ("Electricity", "Heat" or both).
        """

        self.property_ids = property_ids
        self.start_time = start_time
        self.end_time = end_time
        self.energy_type = ["Heat", "Electricity"]

        start_year = start_time.year
        end_year = end_time.year
        year_difference = end_year - start_year

        years = []
        for y in range(year_difference + 1):
            years.append(start_year + y)

        bas_df = self.retrievePropertiesConsumptionByYear(property_ids, years)

        if not bas_df.empty:

            self.replaceTime(bas_df)

            self.translateConsumption(bas_df)

            bas_df = self.selectTimeObservation(bas_df, start_time, end_time)

            if dropna:
                bas_df.dropna(inplace=True)

            # if only one energy type is selected, we have to drop columns which energy type isn't valid anymore
            """if len(self.energy_type)<2:
                if "Heat" in energy_type or "heat" in energy_type:
                    bas_df = bas_df[bas_df["consumption_measure"] == 'Heat']
                elif "Electricity" in energy_type or "electricity" in energy_type:
                    bas_df = bas_df[bas_df["consumption_measure"] == 'Electricity']
                else:
                    print("You type an invalid consumption measure type.")"""
            # TODO error exception

            self.consumption_df = bas_df

        else:
            column_names = ['property_id', 'property_internal_id', 'property_name',
                            'consumption_measure', 'consumption', 'keyfield', 'datetime']
            self.consumption_df = pd.DataFrame(columns=column_names)

    def getMeanEnergyByProperty(self, single_id):
        """
        Returns the average (heat and electricity if both are selected) consumption of one property (chosen by its id)
        """
        energy_types = self.energy_type
        energy_means = []

        single_id_df = self.consumption_df[self.consumption_df["property_id"] == single_id]

        for energy_type in energy_types:
            energy_df = single_id_df[(single_id_df["consumption_measure"] == energy_type)]

            energy_means.append(energy_df["consumption"].mean())

        return energy_means

    # Abandoned for now
    def getMeanEnergyByPropertyDF(self, single_id):
        """
        Returns the average (heat and electricity if both are selected) consumption of one property (chosen by its id) as a Dataframe
        """
        energy_types = self.energy_type
        energy_means = []

        single_id_df = self.consumption_df[self.consumption_df["property_id"] == single_id]


    def retrievePropertiesConsumptionByYear(self, ids, years):
        """
        Return a dataframe containing the energy consumption of properties listed by their ids during certain years
        """

        def my_query(args):
            """
            Format a query using args: (id, year).
            """
            query = (hourly_url
                     + "?property_id=eq."
                     + str(args[0])
                     + "&year=eq."
                     + str(args[1])
                     )
            return query

        q_args = product(ids, years)
        # form a query per each id+year combination:
        queries = [my_query(p) for p in q_args]
        dfs = [pd.read_json(q) for q in queries]  # fetch data for each query

        return pd.concat(dfs)


    def replaceTime(self, df):
        """
        replace the four columns of time (year, month, day and hour) by only one normalized column using datetime library
        """

        # Saving times
        timeDf = df[["year", "month", "day", "starting_hour"]].values.tolist()

        # COnverting to datetime type
        new_time_list = [datetime(time[0], time[1], time[2], time[3]) for time in timeDf]

        # Deleting obsolete columns
        df.drop("year", axis=1, inplace=True)
        df.drop("month", axis=1, inplace=True)
        df.drop("day", axis=1, inplace=True)
        df.drop("starting_hour", axis=1, inplace=True)

        # Putting the new normalized column to the df
        df["datetime"] = new_time_list
        df.sort_values(by="datetime")


    def selectTimeObservation(self, df, start_time, end_time):
        """
        Returns the dataframe df during a more precise time interval [start_time, end_time],
        with the hour, the day, the month and the year.
        """
        return df.loc[(df['datetime'] >= start_time) & (df['datetime'] < end_time)]


    def translateConsumption(self, df):
        df["consumption_measure"].replace({"Lämpö": "Heat", "Sähkö": "Electricity"}, inplace=True)


# Test
"""start_date = datetime(2018, 1, 1, 0)
end_date = datetime(2020, 1, 1, 0)
ids = [657701, 619401]

retro = Retrospective(ids, start_date, end_date)

retro.consumption_df.info()

print("Properties' id")
print(retro.consumption_df["property_id"].value_counts(dropna=False))

print("Consumption average of property 622506")
print(retro.getMeanEnergyByProperty(622506))

print("Consumption average of property 619401")
print(retro.getMeanEnergyByProperty(619401))"""
