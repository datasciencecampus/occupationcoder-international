# occupationcoder-international
[![stability-beta](https://img.shields.io/badge/stability-beta-33bbff.svg)](https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#beta)

## A tool to assign standard occupational classification codes to job descriptions

This repository is a development to the code included in the Python package [`occupationcoder`](https://github.com/aeturrell/occupationcoder), with the original codebase by Jyldyz Djumalieva, [Arthur
Turrell](http://aeturrell.github.io/home), David Copple, James
Thurgood, and Bradley Speigner.

This updated version `occupationcoder` adds functionality to code job descriptions to the [International Standard Classification of Occupations 2008 (ISCO)](https://www.ilo.org/public/english/bureau/stat/isco/isco08/), while retaining original functionality for the UK 3-digit [Standard Occupational Classification (SOC) coding scheme](https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc).

In addition, this update includes functionality ([build_dict.py](occupationcoder/createdictionaries/build_dict.py)) to create custom dictionaries for other coding schemes, provided a suitable input format. We provide a [.ipynb notebook that demonstrates how to use this](occupationcoder/notebooks/building_custom_dictionaries.ipynb).
We cannot guarantee the effectiveness of this method with other coding schemes due to the differences between coding schemes, particularly in terms of scheme layout and detail available.

## DISCLAIMER
The code contained within this repository is provided 'as is'. We stress that -

1. Any **use of this code is entirely at the risk of the user**, and users are fully responsible for checking whether the codebase is suitable for their use case, as well as the quality and accuracy of any outputs generated.
2.  The __dictionaries included in this repositories are provided as examples only and should not be considered as official versions of any occupation coding scheme: it is the sole responsibility of the user of this codebase to check whether the dictionaries used are correct and suitable for their use case__.
3. (Co) authors of this codebase at the Office for National Statistics Data Science Campus do not commit to responding to requests for additional features or long-term maintenance of the codebase.
4. This approach to occupation coding has only been tested with data written in English, we cannot guarantee it will work for other languages.

Please see CONTRUTING.md for furthe details on expected maintenance, bugs etc.

## Using `occupationcoder`

In contrast to the original package, as presented here, we assume the user will code  inputs provided as a .csv file as opposed to coding single job descriptions (if a single record is to be coded, it is fine to just code an input file with a single record). Information on how to format inputs, run the tool, and a summary of expected outputs is provided below.

### Getting started

After cloning the repository locally, we suggest setting up a new virtual environment to house necessary packages (e.g. `python -m venv .coder-env` and activate this as appropriate for your OS).

To install dependencies and set up the package locally, run the following in a command line interface, in the base directory of this repository (i.e. where this README.md is located):
```
pip install -r requirements.txt
python setup.py install
```

### Input format

Expected data input is as per the [tests/test_vacancies.csv](tests/test_vacancies.csv) file. Three columns, with headers and content as follows:
- `job_title`: Specific title of the job to code. `occupationcoder` will use this to attempt an exact match against any specific job titles listed in the target scheme. This is the only field that is treated separately and used for an attempt at an exact match.
- `job_description`: Expected to be a extended description of the given job, including e.g. tasks or further context. E.g. where `job_title` is "dentist", `job_description` might be "providing dental care to patients".
- `job_sector`: industrial/sectoral description for the given job. E.g. "medical".

For each row in the input data set, `occupationcoder` will attempt to find an exact match in the given coding scheme. If one is found, the appropriate code from the coding scheme will be returned.
If no exact match is found, three best "fuzzy" matches using TF-IDF will be returned, using information combined from `job_title`, `job_description` and `job_sector`.

### Running in the command line

To code the example input file from the command line, use the following (note that by not supplying a value for the `scheme` argument, this codes to the default scheme, which is SOC):

```
python occupationcoder/coder.py --in_file="tests/test_vacancies.csv"
```
Adjust the value given for the `in_file` argument to code a different input file.

To code to the ISCO coding scheme instead, use the `scheme` parameter:
```
python occupationcoder/coder.py --in_file="tests/test_vacancies.csv" --scheme="isco"
```
Note that the `scheme` arguments looks for a directory with the same name under [occupationcoder/dictionaries](occupationcoder/dictionaries/). Out of the box, we provide the dictionaries for the SOC scheme as used by the original package, and we have added corresponding ISCO dictionaries.

> The __dictionaries included in this repositories are provided as examples only and should not be considered as official versions of any occupation coding scheme: it is the sole responsibility of the user of this codebase to check whether the dictionaries used are correct and suitable for their use case__.

By default, [coder.py](occupationcoder/coder.py) provides "long" output, i.e. including TF-IDF scores for each fuzzy prediction (note that these are not given if an exact match is found). To suppress outputting scores, set the `output` argument to "single" instead of "multi":
```
python occupationcoder/coder.py --in_file="tests/test_vacancies.csv" --scheme="isco" --output="single"
```

For a full description of all available arguments in `coder.py`:
```
python occupationcoder/coder.py --help
```

## Creating custom or bespoke dictionaries from coding schemes

The current repository provides example dictionaries to allow coding to SOC and ISCO schemes. Although these work and and be used to code given occupations to (as specified above and using the `scheme` argument for [coder.py](occupationcoder/coder.py)), they should be considered examples only and it is the responsibility of the user to check that the codes used are correct and suitable for their given use case.

We have provided code and functionality to create bespoke dictionaries from coding schemes (provided the latter are presented in a suitable format). The Python code for this can be found in [build_dict.py](occupationcoder/createdictionaries/build_dict.py); to illustrate its use we have presented a Jupyter notebook [building_custom_dictionaries.ipynb](occupationcoder/notebooks/building_custom_dictionaries.ipynb). Any use of this, again, is at the users' own risk.

When placed in the subdirectories of the [dictionaries](occupationcoder/dictionaries/) folder, custom dictionaries (formatted as .json files) should be accessible by using the respective subdirectory name as the value for the `scheme` parameter for `coder.py`. (e.g. `coder.py --in_file="my_input_file.csv" --scheme="my_custom_scheme"`).

## Pre-requisites

All required packages are specified in [requirements.txt](requirements.txt).

## Testing

Assuming [setup.py](setup.py) has been run as above, to run the tests in your virtual environment, use

```
python -m unittest
```

in the top level occupationcoder directory.
Look in [test_occupationcoder.py](tests/test_occupationcoder.py) for what is run and for examples of use. The output appears in the [processed_jobs.csv](/occupationcoder/outputs/processed_jobs.csv) file in the [outputs](./occupationcoder/outputs/) folder.

## Credits

As above, this is a development based on `occupationcoder` authored by Jyldyz Djumalieva, [Arthur Turrell](http://aeturrell.github.io/home), David Copple, James
Thurgood, Bradley Speigner and Martin Wood.
