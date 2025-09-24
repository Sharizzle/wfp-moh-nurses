from pathlib import Path
import pandas as pd
from datetime import datetime

def read_csv(filename: str, data_dir: Path = Path("data")) -> pd.DataFrame:
    """
    Read a CSV file from the data folder (default) with pyarrow backend.
    """
    path = data_dir / filename
    df = pd.read_csv(path, dtype_backend="pyarrow")
    return df


def write_csv(
    df: pd.DataFrame,
    filename: str,
    output_dir: Path = Path("output"),
    timestamp: bool = False,
    **kwargs
) -> Path:
    """
    Write a DataFrame to a CSV file in the output folder (default).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to write
    filename : str
        Name of the output CSV file (e.g., "schools_out.csv")
    output_dir : Path, optional
        Base directory where the CSV will be saved (default: ./output)
    timestamp : bool, optional
        If True, prepend a timestamp to the file name (default: False)
    kwargs : dict
        Extra keyword arguments passed to `DataFrame.to_csv`

    Returns
    -------
    Path
        Full path of the written file
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if timestamp:
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"{ts}_{filename}"

    path = output_dir / filename
    df.to_csv(path, index=False, **kwargs)
    return path
