# -*- coding: utf-8 -*-
"""Main module."""

import json
import time
import pandas as pd

from pathlib import Path

# NLP related packages to support fuzzy-matching
from occupationcoder import cleaner
from rapidfuzz import process, fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from argparse import ArgumentParser

# For preventing windows multiprocessing error
from multiprocessing import freeze_support

config = cleaner.load_config()

script_dir = Path(config["dirs"]["script_dir"])
parent_dir = Path(config["dirs"]["parent_dir"])
lookup_dir = Path(config["dirs"]["lookup_dir"])
output_dir = Path(config["dirs"]["output_dir"])


class Coder:
    def __init__(
        self,
        lookup_dir=lookup_dir,
        scheme=config["user"]["scheme"],
        output=config["user"]["output"],
    ):
        """
        Main class initialiser

        Keyword arguments:
        lookup_dir:str
            string containing directory where scheme classification found
        scheme:str
            string containing scheme
        output:str
            string containing directory where all outputs to be placed
        """
        self.scheme = scheme.lower()
        self.output = output
        self.cl = cleaner.Cleaner(scheme=self.scheme)
        # Load up the titles lists, ensure codes are loaded as strings...
        with open(
            lookup_dir / f"{self.scheme}/titles_{self.scheme}.json", "r"
        ) as infile:
            self.titles_mg = json.load(infile, parse_int=str)

        # Clean the job titles lists with the same code as for records
        for code in self.titles_mg.keys():
            self.titles_mg[code] = [
                self.cl.simple_clean(title, known_only=False)
                for title in self.titles_mg[code]
            ]

        self.mg_buckets = pd.read_json(
            lookup_dir / f"{self.scheme}/buckets_{self.scheme}.json"
        ).astype(str)

        # Build the TF-IDF model
        self._tfidf = TfidfVectorizer(stop_words="english", ngram_range=(1, 3))

        # Store the matrix of TF-IDF vectors
        self._tfidf_matrix = self._tfidf.fit_transform(self.mg_buckets.Titles_nospace)

        # Placeholder, column names for fields needed for coding
        self.df_columns = {"title": None, "sector": None, "description": None}

    def get_exact_match(self, title: str):
        """ If it exists, finds exact match to a job title's first three words

        Returns: Associated dictionary code for the exact match
        """
        title = " ".join(title.split()[:3])
        result = None
        keys = self.titles_mg.keys()

        # For each  code:
        for k in keys:
            # Check if exact job title is in its list of job titles
            if title in self.titles_mg[k]:
                result = k
        return result

    def get_tfidf_match(self, text, top_n=5):
        """
        Finds the closest top_n matching coding scheme descriptions to some text

        Keyword arguments:
            text -- str. input text to match.
            top_n -- num. top N to return. Default 5.
        Returns:
            list of best matching scheme codes, of length top_n
        """

        # Calculate similarities
        vector = self._tfidf.transform([text])
        sim_scores = cosine_similarity(vector, self._tfidf_matrix)

        # Return top_n highest scoring
        best = sim_scores.argsort()[0, -top_n:]
        scheme_codes = getattr(self.mg_buckets, f"{self.scheme.upper()}_code")
        return [scheme_codes[code] for code in best]

    def get_best_fuzzy_match(self, text: str, candidate_codes):
        """
        Uses partial token set ratio in fuzzywuzzy to check against all
        individual job titles.

        Keyword arguments:
            text -- string, job title, to compare to job titles for codes
            candidate_codes -- list of potential codes worth checking
        Returns:
            Either a list of lists (when self.output = "multi", best
            matching codes and corresponding scores), OR a string (best
            matching code, when self.output = "single").
        """
        options = []

        # Iterate through the best options TF-IDF similarity suggests
        for code in candidate_codes:

            # Clean descriptions
            best_fuzzy_match = process.extractOne(
                text, self.titles_mg[code], scorer=fuzz.token_set_ratio
            )

            # Handle non-match by looking at match score
            if best_fuzzy_match[1] == 0:
                options.append((None, 0, None))
            else:
                # Record best match, the score, and the associated scheme code
                options.append((best_fuzzy_match[0], best_fuzzy_match[1], code))

        # The most probable industries are last - sort so that most probable
        # are first, in case of a draw, max will take first value only
        options.reverse()
        # Order them in terms of confidence level used for 2-3 matches
        best = max(options, key=lambda x: x[1])
        # Return the best code, or top 3
        if self.output == "single":
            return best[2]
        else:
            options.sort(key=lambda x: x[1], reverse=True)
            options = options[:3]
            options_codes = [i[2] for i in options]
            options_scores = [i[1] for i in options]
            options = [options_codes, options_scores]
            return options

    def code_record(self, title: str, sector: str = None, description: str = None):
        """
        Codes an individual job title, with optional sector
        and description text

        Keyword arguments:
            title -- freetext job title to find a code for
            sector -- any additional description of industry/sector
            description -- freetext description of work/role/duties
        Returns:
            list of lists, containing best matches

        """
        clean_title = self.cl.simple_clean(title)

        # Try to code using exact title match (and save a lot of computation
        match = self.get_exact_match(clean_title)
        if match:
            return match

        # Gather all text data
        all_text = clean_title

        # Process sector
        if sector:
            clean_sector = self.cl.simple_clean(sector, known_only=False)
            all_text = all_text + " " + clean_sector

        # Process description
        if description:
            clean_description = self.cl.simple_clean(description, known_only=False)
            all_text = all_text + " " + clean_description

        best_fit_codes = self.get_tfidf_match(all_text)

        # Find best fuzzy match possible with the data
        return self.get_best_fuzzy_match(clean_title, best_fit_codes)

    def _code_row(self, row):
        """
        Helper for applying code_record over the rows of a pandas DataFrame

        Returns: A coded row in a dataframe, to be used as part of `code_data_frame()`

        """
        return self.code_record(
            row[self.df_columns["title"]],
            row[self.df_columns["sector"]],
            row[self.df_columns["description"]],
        )

    def shape_output(self, record_df):
        """
        Add empty columns and rename to contain predicted code for job description and their scores

        Keyword arguments:
            record_df: dataframe where the new columns will be added

        Returns:
            coded_df: dataframe with added columns
        """

        f = lambda x: "prediction {}".format(x + 1)
        coded_df_codes = (
            record_df["Predicted_codes"].apply(pd.Series).fillna("").rename(columns=f)
        )
        f = lambda x: "score {}".format(x + 1)
        coded_df_scores = (
            record_df["Predicted_scores"].apply(pd.Series).fillna("").rename(columns=f)
        )
        record_df = record_df.drop(
            [f"{self.scheme.upper()}_code", "Predicted_scores", "Predicted_codes"],
            axis=1,
        )
        coded_df = pd.concat([record_df, coded_df_codes, coded_df_scores], axis=1)
        return coded_df

    def code_data_frame(
        self,
        record_df,
        title_column: str = "job_title",
        sector_column: str = None,
        description_column: str = None,
    ):
        """
        Applies tool to all rows in a provided pandas DataFrame

        Keyword arguments:
            record_df -- Pandas dataframe containing columns named:
            title_column -- Freetext job title (default 'job_title')
            sector_column -- additional description of industry/sector
                             (default None)
            description_column -- Freetext description of work/role/duties
                                  (default None)
        Returns:
            record_df: Final coded dataframe
        """
        # Record the column names for later
        self.df_columns.update(
            {
                "title": title_column,
                "sector": sector_column,
                "description": description_column,
            }
        )

        record_df[f"{self.scheme.upper()}_code"] = record_df.apply(
            self._code_row, axis=1
        )
        if self.output == "multi":
            has_multi = any(
                isinstance(val, list)
                for val in record_df[f"{self.scheme.upper()}_code"]
            )
            if has_multi:
                record_df["Predicted_scores"] = (
                    record_df[f"{self.scheme.upper()}_code"]
                    .apply(pd.Series)
                    .fillna("")[1]
                )

                record_df["Predicted_codes"] = (
                    record_df[f"{self.scheme.upper()}_code"]
                    .apply(pd.Series)
                    .fillna("")[0]
                )
                record_df = self.shape_output(record_df)
        return record_df

    def parallel_code_data_frame(
        self,
        record_df,
        title_column: str = "job_title",
        sector_column: str = None,
        description_column: str = None,
    ):
        """
        Applies tool to all rows in a provided pandas DataFrame

        Keyword arguments:
            record_df -- Pandas dataframe containing columns named:
            title_column -- Freetext job title to find a code for
                            (default 'job_title')
            sector_column -- Any description of industry/sector (default None)
            description_column -- Freetext description of work/role/duties
                                  (default None)
        """
        # Import within function, makes class/module friendly to systems that
        # don't have modin installed and don't intend to use the function
        import modin.pandas as mpd

        # Initialises something Dask needs to parallelise operations
        from distributed import Client

        client = Client()

        # Record the column names for later
        self.df_columns.update(
            {
                "title": title_column,
                "sector": sector_column,
                "description": description_column,
            }
        )

        # Overwrite to save memory after conversion to Modin DataFrame
        record_df = mpd.DataFrame(record_df)
        record_df["code"] = record_df.apply(self._code_row, axis=1)

        # Hack a private method to convert back to Pandas DataFrame
        result = record_df._to_pandas()
        client.close()
        return result


def parse_cli_input():
    """
    Parses CLI arguments, setting defaults from config.yml if not explicitly supplied.

    Keyword arguments:
        None

    Returns:
        args: dict of arguments
    """
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "--in_file", help="Input file to code", default=config["user"]["input_file"]
    )
    arg_parser.add_argument(
        "--title_col",
        help="Column name containing job title",
        default=config["user"]["title_column"],
    )
    arg_parser.add_argument(
        "--sector_col",
        help="Column name containing sector description",
        default=config["user"]["sector_column"],
    )
    arg_parser.add_argument(
        "--description_col",
        help="Column name containing job description",
        default=config["user"]["description_column"],
    )
    arg_parser.add_argument(
        "--scheme", help="Scheme to code to", default=config["user"]["scheme"]
    )
    arg_parser.add_argument(
        "--out_file", help="Output file name", default=config["user"]["output_file"]
    )
    arg_parser.add_argument(
        "--output",
        help="Type of Outputs: single or multi",
        default=config["user"]["output"],
    )
    args = arg_parser.parse_args()
    print("\nRunning coder with the following settings:\n")
    print("Input file: " + args.in_file)
    print("Coding to scheme: " + args.scheme)
    print("Output type: " + args.output)
    print("Data column job titles: " + args.title_col)
    print("Data column job sector: " + args.sector_col)
    print("Data column job description: " + args.description_col)
    print("Output file: " + args.out_file + "\n")
    return args


# Define main function. Main operations are placed here to make it possible
# use multiprocessing in Windows.
if __name__ == "__main__":
    freeze_support()

    args = parse_cli_input()

    # Read command line inputs
    df = pd.read_csv(args.in_file)
    commCoder = Coder(scheme=args.scheme, output=args.output)
    proc_tic = time.perf_counter()
    df = commCoder.code_data_frame(
        df,
        title_column=args.title_col,
        sector_column=args.sector_col,
        description_column=args.description_col,
    )
    proc_toc = time.perf_counter()
    print("Actual coding ran in: {}".format(proc_toc - proc_tic))
    print("occupationcoder message:\n" + "Coding complete. Showing first results...")
    print(df.head())
    # Write to csv
    df.to_csv(output_dir / args.out_file, index=False, encoding="utf-8")
