===============
occupationcoder-ext
===============

A tool to assign standard occupational classification codes to job descriptions
-------------------------------------------------------------------------------

This repository is a development to the code included in the Python package [`occupationcoder`](https://github.com/aeturrell/occupationcoder), with the original codebase by by Jyldyz Djumalieva, [Arthur
Turrell](http://aeturrell.github.io/home), David Copple, James
Thurgood, and Bradley Speigner.

This updated version of the package (1) allows for the coding of job descriptions to the [International Standard Classification of Occupations 2008 (ISCO)](https://www.ilo.org/public/english/bureau/stat/isco/isco08/), while retaining original functionality for the UK 3-digit [Standard Occupational Classification (SOC) coding scheme](https://www.ons.gov.uk/methodology/classificationsandstandards/standardoccupationalclassificationsoc); and (2) provides additional functionality to generate suitable dictionaries for the coding to any other arbitrary coding scheme, provided the scheme is supplied in a similar acceptable format.

For coding to schemes other than SOC or ISCO, there is a README <filename> That outlines how to build your own dictionaries for use in this system.
We cannot guarantee the effectiveness of this method with other coding schemes due to the nature of differing detail between schemes.

**Disclaimer**
~~~~~~~~~~

The code contained within this repository is provided 'as is' for the purpose of coding survey data to international coding schemes.
We stress that -
1. Any **use of this code is entirely at the risk of the user**, and users are fully responsible for checking whether the codebase is suitable for their use case, as well as the quality and accuracy of any outputs generated.
2. (Co) authors of this codebase at the Office for National Statistics Data Science Campus do not commit to responding to requests for additional features or long-term maintenance of the codebase. The code is provided 'as is'.
3. This approach to occupation coding has only been tested with data written in English, we cannot guarantee it will work for other languages.


Pre-requisites
~~~~~~~~~~~~~~

See `requirements.txt` for a full list of Python packages.

occupationcoder is built on top of `NLTK <http://www.nltk.org/>`__ and
uses 'Wordnet' (a corpora, number 82 on their list) and the Punkt
Tokenizer Models (number 106 on their list). When the coder is run, it
will expect to find these in their usual directories. If you have nltk
installed, you can get them corpora using ``nltk.download()`` which will
install them in the right directories or you can go to
`http://www.nltk.org/nltk_data/ <http://www.nltk.org/nltk_data/>`__ to
download them manually (and follow the install instructions).

A couple of the other packages, such as
`rapidfuzz <https://pypi.org/project/rapidfuzz/>`__ do not come
with the Anaconda distribution of Python. You can install these via pip
(if you have access to the internet) or download the relevant binaries
and install them manually.

File and folder description - NEEDS UPDATING FOR NEW FOLDER STRUCTURE = COPY FROM NORMAL NSA PACKAGE AND MAKE ADJUSTMENTS
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  ``occupationcoder/coder.py`` applies SOC codes to job descriptions
-  ``occupationcoder/cleaner.py`` contains helper function which mostly
   manipulate strings
-  ``occupationcoder/createdictionaries`` turns the ONS' index of SOC
   code into dictionaries used by ``occupationcoder/coder.py``
-  ``occupationcoder/dictionaries`` contains the dictionaries used by
   ``occupationcoder/coder.py``
-  ``occupationcoder/outputs`` is the default output directory
-  ``occupationcoder/tests/test_vacancies.csv`` contains 'test' vacancies
   to run the code on, used by unittests, accessible by you!



Running the code as a python script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Importing, and creating an instance, of the coder

.. code-block:: python

    import pandas as pd
    from occupationcoder.coder import SOCCoder
    myCoder = SOCCoder()

To run the code with a single query, use the following syntax with the
``code_record(job_title,job_description,job_sector)`` method:

.. code-block:: python

    if __name__ == '__main__':
        myCoder.code_record('Physicist', 'Calculations of the universe', 'Professional scientific')

Note that you can leave some of the fields blank and the algorithm will still
return a SOC code.

To run the code on a file (eg csv name 'job\_file.csv') with structure

+--------------+-------------------------------------------------------------------------------------------------------------------+---------------------------------------------------+
| job\_title   | job\_description                                                                                                  | job\_sector                                       |
+==============+===================================================================================================================+===================================================+
| Physicist    | Make calculations about the universe, do research, perform experiments and understand the physical environment.   | Professional, scientific & technical activities   |
+--------------+-------------------------------------------------------------------------------------------------------------------+---------------------------------------------------+

use

.. code-block:: python

    df = pd.read_csv('path/to/foo.csv')
    df = myCoder.code_data_frame(df, title_column='job_title', sector_column='job_sector', description_column='job_description')

The column name arguments are optional, shown above are default values.
This will return a new dataframe with SOC code entries appended in a new
column:

+--------------+-------------------------------------------------------------------------------------------------------------------+---------------------------------------------------+-------------+
| job\_title   | job\_description                                                                                                  | job\_sector                                       | SOC\_code   |
+==============+===================================================================================================================+===================================================+=============+
| Physicist    | Make calculations about the universe, do research, perform experiments and understand the physical environment.   | Professional, scientific & technical activities   | 211         |
+--------------+-------------------------------------------------------------------------------------------------------------------+---------------------------------------------------+-------------+

Running the code from the command line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have all the relevant packages in requirements.txt, download the
code and navigate to the occupationcoder folder (which contains the
README). Then run

.. code-block:: shell

    python -m occupationcoder.coder path/to/foo.csv

This will create a 'processed\_jobs.csv' file in the outputs/ folder
which has the original text and an extra 'SOC\_code' column with the
assigned SOC codes.

Testing
~~~~~~~

To run the tests in your virtual environment, use

.. code-block:: shell

    python -m unittest

in the top level occupationcoder directory. Look in ``test_occupationcoder.py`` for what is run and for examples of use. The output appears in the 'processed\_jobs.csv' file in the outputs/
folder.


Credits
-------

The development of this package was supported by the Bank of England.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
