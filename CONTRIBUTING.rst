.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

# Not committing to new comments, especially new feature requests.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at #ADD WHEN WE KNOW WHERE THIS IS BEING STORED (i.e. DSC/OCCCOCDER2.0)

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with "enhancement"
and "help wanted" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

occupationcoder could always use more documentation, whether as part of the
official occupationcoder docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at #ADD WHEN WE KNOW WHERE THIS IS BEING STORED (i.e. DSC/OCCCOCDER2.0)

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `occupationcoder` for local development.

1. Fork the `occupationcoder` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/occupationcoder.git

3. Create a virtualenv for development. The following steps assume the use of the venv library:

    $ python3 -m venv occupationcoder

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. This repository makes use of pre-commit hooks. If approaching this project as a developer, 
   you can install and enable pre-commit by running the following in your shell:

    $ pip install pre-commit
    $ Enable pre-commit: Ensure you at the base repository level and run:
    $ pre-commit install

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.

Tips
----

To run a subset of tests::


    $ python -m unittest tests.test_occupationcoder

