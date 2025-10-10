#!/usr/bin/env python

"""Tests for `occupationcoder` package."""

import unittest
from unittest.mock import patch
import time
import sys
import subprocess

import pandas as pd
from importlib.resources import files
from oc3i import coder, cleaner
from oc3i.coder import parse_cli_input

config = cleaner.load_config()


class TestParseCliInput(unittest.TestCase):

    @patch('sys.argv', [
        'script_name',
        '--in_file', 'input.csv',
        '--title_col', 'job_title',
        '--sector_col', 'industry',
        '--description_col', 'desc',
        '--scheme', 'SOC2020',
        '--out_file', 'output.csv',
        '--output', 'multi',
        '--get_titles', 'best'
    ])
    def test_all_arguments_provided(self):
        args = parse_cli_input()
        self.assertEqual(args.in_file, 'input.csv')
        self.assertEqual(args.title_col, 'job_title')
        self.assertEqual(args.sector_col, 'industry')
        self.assertEqual(args.description_col, 'desc')
        self.assertEqual(args.scheme, 'SOC2020')
        self.assertEqual(args.out_file, 'output.csv')
        self.assertEqual(args.output, 'multi')
        self.assertEqual(args.get_titles, 'best')

    @patch('sys.argv', ['script_name', '--in_file', 'input.csv'])
    def test_partial_arguments_provided(self):
        args = parse_cli_input()
        self.assertEqual(args.in_file, 'input.csv')
        self.assertEqual(args.title_col, config["user"]["title_column"])
        self.assertEqual(args.sector_col, config["user"]["sector_column"])
        self.assertEqual(args.description_col, config["user"]["description_column"])
        self.assertEqual(args.scheme, config["user"]["scheme"])
        self.assertIsNone(args.out_file)
        self.assertEqual(args.output, config["user"]["output"])
        self.assertEqual(args.get_titles, config["user"]["get_titles"])

    @patch('sys.argv', ['script_name'])
    def test_no_arguments_provided(self):
        args = parse_cli_input()
        self.assertIsNone(args.in_file)
        self.assertEqual(args.title_col, config["user"]["title_column"])
        self.assertEqual(args.sector_col, config["user"]["sector_column"])
        self.assertEqual(args.description_col, config["user"]["description_column"])
        self.assertEqual(args.scheme, config["user"]["scheme"])
        self.assertIsNone(args.out_file)
        self.assertEqual(args.output, config["user"]["output"])
        self.assertEqual(args.get_titles, config["user"]["get_titles"])

class TestOccupationcoder(unittest.TestCase):
    """Tests for `occupationcoder` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        # The expected cleaned titles to our test data
        self.expected_titles = ["physicist", "economist", "ground worker"]
        # The SOC codes that TFIDF is expected to suggest for three examples
        self.expected_codes = [
            "242",
            "311",
            "212",
            "215",
            "211",
            "353",
            "412",
            "215",
            "242",
            "211",
            "242",
            "533",
            "243",
            "912",
            "323",
        ]

        # Load the three example records
        self.test_df = pd.read_csv(files("oc3i.data") / "test_vacancies.csv")

        # Instantiate matching class
        self.matcher = coder.Coder(scheme="soc", output="single")
        self.isco_matcher = coder.Coder(scheme="isco")
        self.cl = cleaner.Cleaner()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_clean_titles(self):
        """Checks that results of title cleaning are as expected"""
        clean_titles = self.test_df["job_title"].apply(self.cl.simple_clean)
        for title in clean_titles:
            self.assertIn(title, self.expected_titles)

    def test_code_exact_matcher(self):
        """Results of exact title matching"""
        clean_titles = self.test_df["job_title"].apply(self.cl.simple_clean)
        matches = clean_titles.apply(self.matcher.get_exact_match)
        for match in matches:
            self.assertIn(match, ["211", "242", None])

    def test_isco_exact_match(self):
        """Tests the ability for coder to access ISCO dictionaries correctly"""
        clean_titles = self.test_df["job_title"].apply(self.cl.simple_clean)
        matches = clean_titles.apply(self.isco_matcher.get_exact_match)
        for match in matches:
            self.assertIn(match, ["2111", "2631", None])

    def test_code_tfidf_matcher(self):
        """TF-IDF similarity suggestions for categories?"""
        df = self.test_df.copy()
        df["clean_title"] = df["job_title"].apply(self.cl.simple_clean)
        df["clean_sector"] = df["job_sector"].apply(
            lambda x: self.cl.simple_clean(x, known_only=False)
        )
        df["clean_desc"] = df["job_description"].apply(
            lambda x: self.cl.simple_clean(x, known_only=False)
        )
        for index, row in df.iterrows():
            clean = " ".join(
                [row["clean_title"], row["clean_sector"], row["clean_desc"]]
            )
            SOC_codes = self.matcher.get_tfidf_match(clean)
            for code in SOC_codes:
                self.assertIn(code, self.expected_codes)

    def test_code_record(self):
        """Confirm it correctly runs on our example single record"""
        result = self.matcher.code_record(
            title="Physicist",
            sector="Professional scientific",
            description="Calculations of the universe",
        )

        self.assertEqual(result, "211")

    def test_code_data_frame(self):
        """Running the included examples from a file."""
        df = pd.read_csv(files("oc3i.data") / "test_vacancies.csv")
        df = self.matcher.code_data_frame(
            df,
            title_column="job_title",
            sector_column="job_sector",
            description_column="job_description",
        )
        self.assertEqual(df["SOC_code"].to_list(), ["211", "242", "912"])

    def test_multi_code_output(self):
        """Running samples from file and getting codes and scores out using ISCO"""
        df = pd.read_csv(files("oc3i.data") / "test_vacancies.csv")
        df = self.isco_matcher.code_data_frame(
            df,
            title_column="job_title",
            sector_column="job_sector",
            description_column="job_description",
        )
        self.assertEqual(df["prediction 1"].to_list(), ["2111", "2631", "3333"])

    def test_command_line(self):
        """Test code execution at command line"""

        # sys.executable returns current python executable, ensures code is run
        # in same environment from which tests are called
        subprocess.run(
            [
                sys.executable,
                "-m",
                "oc3i.coder",
                "--scheme=soc",
                "--output=single",
            ]
        )
        df = pd.read_csv("output.csv")
        self.assertEqual(df["SOC_code"].to_list(), [211, 242, 912])

    def test_get_code_name(self):
        testing = pd.Series(["1111", "2151", "4132", "7221", "9111"])
        expected = ["Legislators", 
                    "Electrical Engineers", 
                    "Data Entry Clerks", 
                    "Blacksmiths, Hammersmiths and Forging Press Workers", 
                    "Domestic Cleaners and Helpers"]
        results = testing.map(self.isco_matcher.get_code_name)
        self.assertEqual(list(results), expected)

