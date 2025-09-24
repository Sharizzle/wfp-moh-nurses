import config
import pandas as pd

def main():
    # Grab current year from config settings
    print(f"Current Year: {config.current_year}")

if __name__ == "__main__":
    main()