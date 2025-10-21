import pandas as pd

# Import Functions
import config
import io_read_write
import wrangle

def main():
    # General Information
    print(f"Current Year: {config.CURRENT_YEAR}")
    print(f"Projection Year: {config.PROJECTION_LAST_YEAR}")

    # Import Data Required
    df_nursing_services = io_read_write.read_xlsx("./MoH_Model_Input.xlsx", sheet_name="Nursing Services")
    df_benchmarks = io_read_write.read_xlsx("./MoH_Model_Input.xlsx", sheet_name="Benchmarks")

    df_nursing_services = wrangle.normalize_column_names(df_nursing_services)
    df_benchmarks = wrangle.normalize_column_names(df_benchmarks)

if __name__ == "__main__":
    main()