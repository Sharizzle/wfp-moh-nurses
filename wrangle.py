import pandas as pd

def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names to snake_case:
    - Strip leading/trailing spaces
    - Lowercase everything
    - Replace spaces and hyphens with underscores
    - Remove duplicate underscores
    - Remove non-alphanumeric characters (except underscores)

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame with normalized column names.
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()                      # remove leading/trailing spaces
        .str.lower()                      # lowercase
        .str.replace(r"[ \-]+", "_", regex=True)   # spaces/hyphens → underscore
        .str.replace(r"[^\w_]", "", regex=True)    # drop non-alphanumeric
        .str.replace(r"__+", "_", regex=True)      # collapse multiple underscores
        .str.strip("_")                   # remove leading/trailing underscores
    )
    return df

def rename_columns(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """
    Rename columns using a dictionary {old: new}.
    """
    return df.rename(columns=mapping)

def missing_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a summary of missing values by column.
    """
    return (
        df.isna()
        .sum()
        .reset_index(name="missing")
        .rename(columns={"index": "column"})
        .assign(
            total=len(df),
            pct=lambda d: d["missing"] / d["total"] * 100
        )
        .sort_values("pct", ascending=False)
        .reset_index(drop=True)
    )

def rename_values(df: pd.DataFrame, col: str, mapping: dict) -> pd.DataFrame:
    """
    Map messy category values to clean ones.
    Example: {"M": "Male", "male": "Male", "F": "Female"}
    """
    df = df.copy()
    df[col] = df[col].replace(mapping)
    return df

def fill_missing(df: pd.DataFrame, fill_map: dict) -> pd.DataFrame:
    """
    Fill missing values using a column: value map.
    Example: {"age": 0, "city": "unknown"}
    """
    return df.fillna(fill_map)

def drop_rows_by_value(df: pd.DataFrame, column: str, value) -> pd.DataFrame:
    """
    Remove every row where `column` equals `value`.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    column : str
        Column name to check.
    value : any
        Value to match. All rows where df[column] == value are dropped.

    Returns
    -------
    pd.DataFrame
        DataFrame without the matching rows.
    """
    df = df.copy()
    return df[df[column] != value].reset_index(drop=True)

def drop_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """
    Drop specified columns from a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    columns : list[str]
        List of column names to drop.

    Returns
    -------
    pd.DataFrame
        DataFrame without the specified columns.
    """
    return df.drop(columns=columns, errors="ignore")