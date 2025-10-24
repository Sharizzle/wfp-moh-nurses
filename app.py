# %% [markdown]
# # Imports

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Import Functions
import config
import io_read_write
import wrangle
import columns
import helpers

# Import Data Required
df_nursing_services = io_read_write.read_xlsx("./MoH_Model_Input.xlsx", sheet_name="Nursing Services")
df_benchmarks = io_read_write.read_xlsx("./MoH_Model_Input.xlsx", sheet_name="Benchmarks")
df_health_clusters = io_read_write.read_xlsx("./MoH_Model_Input.xlsx", sheet_name="Health Clusters")
df_demand_data_input = io_read_write.read_xlsx("./MoH_Model_Input.xlsx", sheet_name="Demand Data by Speciality")
df_scenario_criteria = io_read_write.read_xlsx("./MoH_Model_Input.xlsx", sheet_name="Scenarios")

# Melt Relevant Datasets
df_demand_data = df_demand_data_input.melt(
    id_vars=[helpers.denormalize_text(columns.PATIENT_CARE_AREA), helpers.denormalize_text(columns.NURSING_SERVICE), helpers.denormalize_text(columns.SELECTED_DRIVER)],
    var_name="Cluster",
    value_name=columns.DRIVER_VALUE
)

# Normalize Column Names
df_nursing_services = wrangle.normalize_column_names(df_nursing_services)
df_benchmarks = wrangle.normalize_column_names(df_benchmarks)
df_health_clusters = wrangle.normalize_column_names(df_health_clusters)
df_demand_data = wrangle.normalize_column_names(df_demand_data)
df_scenario_criteria = wrangle.normalize_column_names(df_scenario_criteria)

# %% [markdown]
# # Generate Benchmarks

# %%
_additional_quantiles = [q for q in df_scenario_criteria[columns.PERCENTILE_VALUE].tolist() if q not in [0.25, 0.5, 0.75]]

df_benchmarks_stats = (
    df_benchmarks
    .groupby([columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE, columns.DRIVER], dropna=False)
    .apply(helpers.calc_stats, value_col=columns.RATIO_VALUE, include_groups=False)
    .reset_index()
)

df_avg_ratio_by_area_country = (
    df_benchmarks
    .groupby([columns.COUNTRY, columns.PATIENT_CARE_AREA], dropna=False)
    [columns.RATIO_VALUE]
    .mean()
    .reset_index()
    .rename(columns={columns.RATIO_VALUE: columns.AVERAGE_RATIO_VALUE})
)

df_avg_overall_ratio_by_country = (
    df_benchmarks
    [df_benchmarks[columns.PATIENT_CARE_AREA] == "Overall"]
    .groupby([columns.COUNTRY], dropna=False)
    [columns.RATIO_VALUE]
    .mean()
    .reset_index()
    .rename(columns={columns.RATIO_VALUE: columns.AVERAGE_RATIO_VALUE})
)

df_benchmarks_scenarios = (
    df_benchmarks
    [df_benchmarks[columns.PATIENT_CARE_AREA] != "Overall"]
    .groupby([columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE, columns.DRIVER], dropna=False)
    .apply(helpers.calc_stats_scenarios, quantiles = df_scenario_criteria[columns.PERCENTILE_VALUE].tolist(), value_col=columns.RATIO_VALUE, include_groups=False)
    .reset_index()
).drop(columns=["level_3"])

df_benchmarks_scenarios[columns.SELECTED_DRIVER] = (
    df_benchmarks_scenarios[columns.DRIVER]
    .astype(str)
    .str.split(" /", n=1)
    .str[1]
    .add("s")
    .str.replace(" ", "", regex=False)
)

# %% [markdown]
# # Calculate Demand Data by Cluster - Current Year

# %%
# Expand nursing services by cluster
df_demand_current_year = wrangle.expand_df_by_values(df = df_nursing_services, new_col = columns.CLUSTER, values = df_health_clusters[columns.CLUSTER].tolist(), as_category = True)
df_demand_current_year[columns.REGION] = wrangle.vlookup_df(left_df = df_demand_current_year, right_df = df_health_clusters, left_on = [columns.CLUSTER], right_on = [columns.CLUSTER], return_col = columns.REGION)


# Grab the driver value from the demand data
df_demand_current_year[columns.DRIVER_VALUE] = wrangle.vlookup_df(left_df = df_demand_current_year, right_df = df_demand_data, left_on = [columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE, columns.SELECTED_DRIVER, columns.CLUSTER], right_on = [columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE, columns.SELECTED_DRIVER, columns.CLUSTER], return_col = columns.DRIVER_VALUE)

# Grab benchmark Value for each scenario
df_demand_current_year = wrangle.expand_df_by_values(df = df_demand_current_year, new_col = columns.SCENARIO_NAME, values = df_scenario_criteria[columns.SCENARIO_NAME].tolist())
df_demand_current_year[columns.PERCENTILE] = wrangle.vlookup_df(left_df = df_demand_current_year, right_df = df_scenario_criteria, left_on = [columns.SCENARIO_NAME], right_on = [columns.SCENARIO_NAME], return_col = columns.PERCENTILE_VALUE)
df_demand_current_year[columns.PERCENTILE] = df_demand_current_year[columns.PERCENTILE].astype(str)

# Grab quartile values
df_demand_current_year[columns.PERCENTILE_VALUE] = wrangle.vlookup_df(left_df = df_demand_current_year, right_df = df_benchmarks_scenarios, left_on = [columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE, columns.SELECTED_DRIVER, columns.PERCENTILE], right_on = [columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE, columns.SELECTED_DRIVER, columns.PERCENTILE], return_col = columns.PERCENTILE_VALUE)
df_demand_current_year[columns.PERCENTILE_VALUE] = df_demand_current_year[columns.PERCENTILE_VALUE].fillna(0)

# Perform calculations
df_demand_current_year[columns.DEMAND] = np.ceil(
    df_demand_current_year[columns.DRIVER_VALUE] * df_demand_current_year[columns.PERCENTILE_VALUE]
).astype(int)

# Distrbute by nursing level
df_demand_current_year[columns.TECHNICIAN_PERCENTAGE] = wrangle.vlookup_df(left_df = df_demand_current_year, right_df = df_nursing_services, left_on = [columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE], right_on = [columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE], return_col = columns.TECHNICIAN_PERCENTAGE)
df_demand_current_year[columns.REGISTERED_NURSE_PERCENTAGE] = wrangle.vlookup_df(left_df = df_demand_current_year, right_df = df_nursing_services, left_on = [columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE], right_on = [columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE], return_col = columns.REGISTERED_NURSE_PERCENTAGE)
df_demand_current_year[columns.APRN_PERCENTAGE] = wrangle.vlookup_df(left_df = df_demand_current_year, right_df = df_nursing_services, left_on = [columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE], right_on = [columns.PATIENT_CARE_AREA, columns.NURSING_SERVICE], return_col = columns.APRN_PERCENTAGE)

df_demand_current_year[columns.TECHNICIAN_DEMAND] = np.floor(df_demand_current_year[columns.DEMAND] * df_demand_current_year[columns.TECHNICIAN_PERCENTAGE]).astype(int)
df_demand_current_year[columns.REGISTERED_NURSE_DEMAND] = np.floor(df_demand_current_year[columns.DEMAND] * df_demand_current_year[columns.REGISTERED_NURSE_PERCENTAGE]).astype(int)
df_demand_current_year[columns.APRN_DEMAND] = np.floor(df_demand_current_year[columns.DEMAND] * df_demand_current_year[columns.APRN_PERCENTAGE]).astype(int)

# Adjust last category (columns.APRN_DEMAND) so row sums never exceed DEMAND
sum_demands = (
    df_demand_current_year[columns.TECHNICIAN_DEMAND] +
    df_demand_current_year[columns.REGISTERED_NURSE_DEMAND] +
    df_demand_current_year[columns.APRN_DEMAND]
)
excess = sum_demands - df_demand_current_year[columns.DEMAND]
df_demand_current_year[columns.APRN_DEMAND] -= excess
df_demand_current_year[columns.APRN_DEMAND] = df_demand_current_year[columns.APRN_DEMAND].clip(lower=0)

# %% [markdown]
# # Save Files

# %%
if config.GENERATE_FILES:
    df_demand_current_year_denorm = wrangle.denormalize_column_names(df_demand_current_year)

    df_output_dictionary = {
        "Output by Cluster by Speciality": df_demand_current_year_denorm,
    }
    
    io_read_write.write_excel_multiple(df_dict = df_output_dictionary, filename = "MoH_Nurses_WFP_Tool_Output.xlsx", timestamp = False)


