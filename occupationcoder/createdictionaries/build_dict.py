import json
import warnings
import re
import pandas as pd
from pathlib import Path
from unidecode import unidecode

from occupationcoder import cleaner

config = cleaner.load_config()
script_dir = Path(config["dirs"]["script_dir"])

cl = cleaner.Cleaner(scheme="")


def aggregate_buckets(
    dataframe, level=None, code_col=None, content_col=None, type=None
):
    """
    Aggregates given dataframe by column code_col across given level (hierarchy in code scheme). Columns specified in content_col are aggregated either into a long character string separated by a space (if type = "buckets") or into a list of strings (if type = "exact").

    Args:
    dataframe (str): dataframe to aggregate
    level (int): hierarchical code scheme level to aggregate into. Should correspond to number of digits in code_col.
    content_col (list): list of str, specifying one or more columns to aggregate.
    type (str, "exact" or "buckets"). If "buckets", values in each column specified in content_col are assumed to be strings, and joined into strings separated by a space. If "exact", values in each column specified in content_col are assumed to be lists of strings and these are concatenated.

    Returns:
        cominbined_df (df): aggregated dataframe

    Examples:
    #

    """
    dataframe = dataframe[dataframe[code_col].str.len() >= level].reset_index()
    dataframe[code_col] = dataframe[code_col].str[:level]
    dataframe = dataframe.fillna("")

    # To ensure aggregation works correctly for both simple strings and lists of strings (as will be the case for "exact match titles").
    # Further allows aggregation for specific columns (content_col) so that this can work for arbitrary scheme data; and uses 'level' to subset.
    if type == "buckets":
        combined_df = (
            dataframe.groupby(code_col)[content_col]
            .agg(lambda x: " ".join(x))
            .reset_index()
        )
    if type == "exact":
        combined_df = (
            dataframe[[code_col, content_col]]
            .groupby(code_col)
            .agg(lambda x: sum(x, []))
            .reset_index()
        )

    return combined_df


def load_file(filename, sheet_name="Sheet1", code_col=None):
    """
    Loads the desired input (coding scheme) file.

    Args: filename (str): Name of the input file. Expects column names in the first row, and as a minimum two
    columns: one including scheme codes, and one containing descriptions of that code (as a minimum, titles for the
    corresponding code). sheet_name (str, optional): Name of the sheet in the input Excel file, if relevant. (
    default: 'Sheet1') code_col (str): Name of the column containing scheme codes.

    Returns:
        df: A Pandas dataframe.

    Examples:
    #    >>> load_file("data/input_data.xlsx", code_col = "codes")

    """
    if code_col is None:
        raise ValueError(
            "Code column not specified. Please indicate which column contains scheme codes."
        )

    # file_path = Path(script_dir) / filename
    df = pd.read_excel(filename, sheet_name=sheet_name, dtype={code_col: str})
    return df


def remove_substr(df_col, exclude_text=None):
    """
    Removes specified text (in exclude_text) from given dataframe column (df_col).
    Assumes exclude_text to be a named dictionary, where the names correspond
    to the name of the given data frame column.
    If exclude_text is not given, an error is raised. If the name of the given column is not included
    in the exclude_text dictionary, nothing is removed.

    Args:
        df_col (Pandas dataframe): Data frame column of text strings.
        exclude_text (dict): Dictionary of lists, with names corresponding to desired column names from
        which to remove text. Each list element is expected to be a substring to be removed.
    Returns:
        A Pandas dataframe column of text strings, which desired substrings removed.

    Example:
        example_df = pd.DataFrame(["hello", "I am", "some really short", "strings"], columns=['Column1'])
        example_text_to_remove = {'Column1':[' really short', 'not relevant'], 'Column2'['this column does not exist']}
        remove_substr(example_df['Column1'], exclude_text = example_text_to_remove)

    """
    if exclude_text is None:
        raise ValueError("No substring to remove specified!")

    if df_col.name in exclude_text:
        exclude = exclude_text[df_col.name]
        for txt in exclude:
            df_col = df_col.apply(lambda x: str(x).replace(txt, ""))
    return df_col


def column_cleaner(df_col):
    """
    Replaces any NaN values from a given dataframe column with a blank string,
    and applies unidecode to deal with any encoding issues in text data.
    Assumes given data frame column is a column of strings.

    Args:
        df_col (Pandas dataframe): column with string text values.
    Returns:
        df_col (Pandas dataframe): column with string text values.

    Example:
        example_df = pd.DataFrame(["hello", "I am", math.nan, "strings"], columns=['Column1'])
        column_cleaner(example_df['Column1'])

    """
    df_col = df_col.fillna("")
    df_col = df_col.apply(unidecode)
    return df_col


def list_exact_titles(titles, min_text_length = 4):
    """
    Helper function to apply simple_clean() on a list consisting of text string elements.
    Addtionally removes any very short text list elements (shorter than min_text_length).
    simple_clean(..., advanced = False) removes HTML tags, removes excess whitespace, keeps only letters and spaces.

    Args:
        titles(list): A list of strings
    Returns:
        A list of strings

    Example:
        # >>> test_list = ["I", "am a", "list of", "strings"]
        # >>> list_exact_titles(test_list)

    """
    result = [cl.simple_clean(s, advanced=False) for s in titles]
    result = [s for s in result if len(s) >= min_text_length]
    return result


def save_json(jsondata, filename=None):
    """
    Saves a given JSON object as a given file.

    Args:
        jsondata (list): A JSON data object
        filename (str): Name for desired output file. By default, output files are placed in a 'dictionaries' subfolder
        in the current calling directory. Filename can be specified as including a further subfolder,
        so filename = 'foo/output.json' will save as './dictionaries/foo/output.json'.
        If either subdirectory substructure does not already exist, it is created.
    Returns:
       Nothing. Error if filename is not supplied.

    Example:
        # >>> save_json(my_json_data, filename = 'foo/output.json')

    """
    if filename is None:
        warnings.warn(
            "Argument 'filename' has not been supplied. Please specifiy output filename.",
            category=Warning,
        )
        return

    filepath = Path(config["dirs"]["lookup_dir"]) / filename
    if not filepath.parent.exists():
        filepath.parent.mkdir()

    with open(filepath, "w") as json_file:
        json.dump(jsondata, json_file, indent=4)


# Takes given Pd dataframe, processes specified columns (calls column_cleaner, simple_clean), puts back into working df
def process_file(
    input_df,
    code_col,
    bucket_cols=[],
    exact_col="",
    exact_col_split="",
    exclude_text={},
    exclude_pattern=None,
    output_files={"buckets": "buckets.json", "exact": "titles.json"},
    bucket_field_names=["code", "description"],
    level=None,
):
    """
    Processes a given dataframe representing a code scheme (codes, descriptions, tasks, etc).
    Iterates through given (sets of) columns.
    The first set is specified by bucket_cols which lists all columns that should be combined into "word buckets"
    corresponding to a given code.
    Each column is cleaned, any substrings specified in exclude_text are removed, hard returns are removed,
    bracketed lists are removed, and all text is cleaned, lowercased, lemmatised, and some synonymns are replaced.
    The output is saved as a JSON that has user-specified names for keys and values, with keys being the scheme codes,
    and values being the corresponding word buckets.

    The second set of columns is optional, and expected to be a single column containing any expected "exact matches"
    where available/applicable, e.g. job titles explicitly listed as being included with a particular scheme code.
    These are processed as above, and exported as a separate JSON with codes for keys and values
    as list of exact columns.

    Args:
        input_df (Pandas dataframe): Input dataframe to process.
        bucket_cols (list): List of strings, corresponding to column names to be processed into word buckets.
        exact_col (str, optional): String, corresponding to dataframe column containing expected exact job title matches
        Default: ''.
        exact_col_split (str, optional): Character string that represents how job title matches in exact_col are to be
        split. Could for example be hard returns ('\n') or dashes ('*). Only needed when exact_col is specified.
        exclude_text (dict, optional): Dictionary of lists of strings, where keys correspond to columns from which
        substrings should be removed, and values are lists of substrings to removed from the given column.
        Only needed if exact_col is specified.
        exclude_pattern (str, optional): Regex expression to remove from any given column.
        output_files (dict): Dictionary specifying output file names for word bucket JSON and exact match JSON outputs
        (if needed). Keys should be specified as 'buckets' and 'exact', and values should be strings of output
        file names. Default: {'buckets': 'buckets.json', 'exact': 'titles.json'}.
        bucket_field_names (list, optional): List of strings specifying field titles in word bucket JSON.
        Defaults: ['code','description'].
        level (list, optional): List of level codes (numbers) to process. If not specified (default: None),
        all levels present in input are included.
    Returns:
        Nothing, saves output as specified JSON files.

    Example:
       # >>>

    """

    # Fuzzy match (bucket) JSON processing:
    buckets_df = input_df.copy()

    for col in bucket_cols:
        buckets_df[col] = column_cleaner(buckets_df[col])
        buckets_df[col] = remove_substr(buckets_df[col], exclude_text=exclude_text)
        if exclude_pattern is not None:
            buckets_df[col] = buckets_df[col].apply(
                lambda x: re.sub(exclude_pattern, "", x)
            )

        buckets_df[col] = buckets_df[col].apply(lambda x: str(x).replace("\n", " "))
        pattern_bracket_list = r"\([a-z]\)"
        buckets_df[col] = buckets_df[col].apply(
            lambda x: re.sub(pattern_bracket_list, "", x)
        )

        buckets_df[col] = buckets_df[col].apply(
            lambda x: cl.simple_clean(x, known_only=False)
        )

    if level == 4:
        buckets_df = buckets_df[buckets_df[code_col].str.len() == level]
        buckets_df = buckets_df.reset_index(drop=True)
    if level < 4:
        buckets_df = aggregate_buckets(
            buckets_df, level, code_col, bucket_cols, type="buckets"
        )

    buckets_code_name = bucket_field_names[0]
    buckets_description_name = bucket_field_names[1]
    buckets_df[buckets_description_name] = buckets_df.apply(
        lambda row: " ".join(row[bucket_cols]), axis=1
    )
    buckets_df[buckets_code_name] = buckets_df[code_col]
    buckets_json = buckets_df[[buckets_code_name, buckets_description_name]].to_dict(
        orient="records"
    )
    save_json(buckets_json, filename=output_files["buckets"])

    # Exact match JSON processing:
    if exact_col != "":
        input_df[exact_col] = remove_substr(
            input_df[exact_col], exclude_text=exclude_text
        )
        input_df[exact_col] = column_cleaner(input_df[exact_col])
        input_df[exact_col] = input_df[exact_col].apply(
            lambda x: x.split(exact_col_split)
        )
        input_df[exact_col] = input_df[exact_col].apply(lambda x: list_exact_titles(x))

        # Remove any levels not desired:
        if level == 4:
            input_df = input_df[input_df[code_col].str.len() == level]
            input_df = input_df.reset_index(drop=True)
        if level < 4:
            input_df = aggregate_buckets(
                input_df, level, code_col=code_col, content_col=exact_col, type="exact"
            )

        exact_json = dict(zip(input_df[code_col], input_df[exact_col]))
        save_json(exact_json, filename=output_files["exact"])


if __name__ == "__main__":
    # print("Please see 'building_custom_dictionaries.ipynb' for information on how to use the functionality in this module.")
    file_name = "data/ISCO-08 EN Structure and definitions.xlsx"
    sheet_name = "ISCO-08 EN Struct and defin"
    code_col = "ISCO 08 Code"
    input_df = load_file(filename=file_name, sheet_name=sheet_name, code_col=code_col)
    exclude_text = {
        "Tasks include": [
            "Tasks performed",
            "Tasks include",
            "Tasks performed by",
            "usually include",
        ],
        "Included occupations": [
            "Examples of the occupations classified here:",
            "Example of the occupations classified here:",
            "Occupations in this major group are classified into the following",
            "Occupations in this sub-major group are classified into the following",
            "Occupations in this minor group are classified into the following",
            "major group",
            "minor group",
            "sub-major group",
            "sub-",
            "unit group",
        ],
    }
    process_file(
        input_df=input_df,
        code_col=code_col,
        bucket_cols=["Title EN", "Definition", "Tasks include"],
        exact_col="Included occupations",
        exact_col_split="\n",
        exclude_text=exclude_text,
        output_files={
            "buckets": "isco/buckets_isco.json",
            "exact": "isco/titles_isco.json",
        },
        bucket_field_names=["ISCO_code", "Titles_nospace"],
        level=4,
    )
