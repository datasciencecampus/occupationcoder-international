# occupationcoder-international
[![stability-beta](https://img.shields.io/badge/stability-beta-33bbff.svg)](https://github.com/mkenney/software-guides/blob/master/STABILITY-BADGES.md#beta)

# A tool to assign standard occupational classification codes to job descriptions

This repository is a development to the code included in the Python package [`occupationcoder`](https://github.com/aeturrell/occupationcoder), with the original codebase by Jyldyz Djumalieva, [Arthur
Turrell](http://aeturrell.github.io/home), David Copple, James
Thurgood, and Bradley Speigner.

This updated version `occupationcoder` adds functionality to code job descriptions to the [International Standard Classification of Occupations 2008 (ISCO)](https://www.ilo.org/public/english/bureau/stat/isco/isco08/), while retaining original functionality for the UK 3-digit [Standard Occupational Classification (SOC) coding scheme](https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc).

In addition, this update includes functionality ([build_dict.py](src/oc3i/createdictionaries/build_dict.py)) to create custom dictionaries for other coding schemes, provided a suitable input format. We provide a [.ipynb notebook that demonstrates how to use this](src/oc3i/notebooks/building_custom_dictionaries.ipynb).
We cannot guarantee the effectiveness of this method with other coding schemes due to the differences between coding schemes, particularly in terms of scheme layout and detail available.

## DISCLAIMER
The code contained within this repository is provided 'as is'. We stress that -

1. Any **use of this code is entirely at the risk of the user**, and users are fully responsible for checking whether the codebase is suitable for their use case, as well as the quality and accuracy of any outputs generated.
2.  The __dictionaries included in this repositories are provided as examples only and should not be considered as official versions of any occupation coding scheme: it is the sole responsibility of the user of this codebase to check whether the dictionaries used are correct and suitable for their use case__.
3. (Co) authors of this codebase at the Office for National Statistics Data Science Campus do not commit to responding to requests for additional features or long-term maintenance of the codebase.
4. This approach to occupation coding has only been tested with data written in English, we cannot guarantee it will work for other languages.

Please see CONTRUTING.md for furthe details on expected maintenance, bugs etc.

# Using `occupationcoder`

In contrast to the original package, as presented here, we assume the user will code  inputs provided as a .csv file as opposed to coding single job descriptions (if a single record is to be coded, it is fine to just code an input file with a single record). Information on how to format inputs, run the tool, and a summary of expected outputs is provided below.

The code in this repository can be used/run either by setting up locally (or in custom cloud infrastructure) by following the steps under "Getting Started" below, or by running in a Github Codespace. We have provided a fully pre-configured set up for this within this repository (in `.devcontainer/`), with all required packages installed, which will allow a user to run the code within a Codespace without any configuration required.  
To start a Codespace, go to to the "Code" button at the top of the Github repository page, select the "Codespaces" tab, and click "Start new codespace" for the relevant branch. Once this is running, for basic use you can follow the steps below from "Input format" onwards.

# Getting started

There are three main ways to use/run the code in this repository: (1) as modules from a Python package in your own script; (2) through use of the included command line script; or (3) through a developer install. Each of these is described below.

## 1. Using as a Python package

The repository is set up for you to use as a Python package. We strongly recommend you using a virtual environment to manage package installs on your setup. Using the following will create a new virtual environment in a folder called `env` in your current working directory:
```
python -m venv env
```
Then you can activate this as appropriate for your OS, e.g. on MacOS/Linux use:
```
source env/bin/activate
```
or on Windows use:
```
source env/Scripts/activate
```

To install the package and its dependencies directly from this repository, use:
```
pip install git+https://github.com/datasciencecampus/occupationcoder-international.git@i12_feat
```

Once installed, you can use `occupationcoder-international` either through the provided Command Line Interface (CLI) script, or by importing and using the package in your own Python code.

An example code snippet that imports package modules and uses this to code example input data provided is as follows:
```
import pandas as pd
from oc3i import Coder
from oc3i.coder import get_example_file

coder = Coder(scheme = "isco")

dat = pd.read_csv(get_example_file())
coder.code_data_frame(dat, 
                      title_column = "job_title", 
                      description_column = "job_description", 
                      sector_column = "job_sector")
```
Note that where the example data is saved locally will depend on your setup; the above uses the function `get_example_file()` to find where it is stored on your system.  
The arguments given for the `code_data_frame()` method (`title_column` etc) are described in the function docstring and should match column names in the input file specificed - see "Settings: coding scheme and input format" below.

### Settings: coding scheme and input format
The `scheme` argument for the `Coder` class looks for a directory with the same name under [occupationcoder/dictionaries](occupationcoder/dictionaries/). Out of the box, we provide the dictionaries for the SOC scheme as used by the original package, and we have added corresponding ISCO dictionaries.  
> The __dictionaries included in this repositories are provided as examples only and should not be considered as official versions of any occupation coding scheme: it is the sole responsibility of the user of this codebase to check whether the dictionaries used are correct and suitable for their use case__.

When coding a data frame, the method `code_data_frame()` expects an input data frame in the format of [test_vacancies.csv](src/oc3i/data/test_vacancies.csv) file. It can have three input columns:

- `job_title`: Specific title of the job to code. `occupationcoder` will use this to attempt an exact match against any specific job titles listed in the target scheme. This is the only field that is treated separately and used for an attempt at an exact match.
- `job_description`: Expected to be a extended description of the given job, including e.g. tasks or further context. E.g. where `job_title` is "dentist", `job_description` might be "providing dental care to patients".
- `job_sector`: industrial/sectoral description for the given job. E.g. "medical".  

As per the example code above, names for each of these columns should be specified as arguments for the `code_data_frame()` method: `title_column`, `description_column` and `sector_column` respectively. The names given need to match the column names in the input data frame.

## 2. Running in the command line

We provide a convenience script (`oc3i`) you can use to directly code a given input file from the command line, producing an output file with the results. This allows use of the coding tool outside of a Python environment, and without needing to write any Python code:
The following CLI command should just run the coder with the default settings and using the example input file provided; it should produce an output file in the current directory also:
```{bash}
oc3i
```
The command line script uses and expects the same input parameters as specificied for the `Coder` class and its `code_data_frame()` method above. 

To code an arbitrary input file in the current directory, to a specific coding scheme (e.g. ISCO), you can use:
```{bash}
oc3i --in_file="my_input_file.csv" --scheme="isco"
```
For a full list of arguments available for the `oc3i` command, use:
```{bash}
oc3i --help
```

## 3. Developer install

To install the package for development, clone this repository in full and run 
```
pip install -e .
```
This should install the package in "editable" mode, allowing you to edit the code and have this reflected when you import the package. You will need to have git installed on your system for this to work. We recommend working in a dedicated virtual environment as per the above.

### Testing

Assuming you have the package installed in editable mode, to run the tests in your virtual environment, run

```
python -m unittest
```

in the top level occupationcoder directory.
Look in [test_occupationcoder.py](tests/test_occupationcoder.py) for what is run and for examples of use. The output appears in the [processed_jobs.csv](/occupationcoder/outputs/processed_jobs.csv) file in the [outputs](./occupationcoder/outputs/) folder.


# Creating custom or bespoke dictionaries from coding schemes

The current repository provides example dictionaries to allow coding to SOC and ISCO schemes. Although these work and and be used to code given occupations to (as specified above and using the `scheme` argument for [coder.py](occupationcoder/coder.py)), they should be considered examples only and it is the responsibility of the user to check that the codes used are correct and suitable for their given use case.

We have provided code and functionality to create bespoke dictionaries from coding schemes (provided the latter are presented in a suitable format). The Python code for this can be found in [build_dict.py](occupationcoder/createdictionaries/build_dict.py); to illustrate its use we have presented a Jupyter notebook [building_custom_dictionaries.ipynb](occupationcoder/notebooks/building_custom_dictionaries.ipynb). Any use of this, again, is at the users' own risk.

When placed in the subdirectories of the [dictionaries](occupationcoder/dictionaries/) folder, custom dictionaries (formatted as .json files) should be accessible by using the respective subdirectory name as the value for the `scheme` parameter for `coder.py`. (e.g. `coder.py --in_file="my_input_file.csv" --scheme="my_custom_scheme"`).

# Credits

As above, this is a development based on `occupationcoder` authored by Jyldyz Djumalieva, [Arthur Turrell](http://aeturrell.github.io/home), David Copple, James
Thurgood, Bradley Speigner and Martin Wood.
