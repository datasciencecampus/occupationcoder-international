# Contributing

We consider this a work-in-progress and you are welcome to continue development.

While authors at the Office for National Statistics Data Science Campus will strive to correct any errors/bugs in the code base as presented, we can not commit to responding to requests for additional features, or to requests for support with specific applications of the code beyond the information provided in the README.

## Reporting bugs

If you are reporting a bug, create an Issue and please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

As above, we cannot commit to implementing any additional functionality.

## Fix Bugs, implementation of new features or continued development

To continue development, we suggest creating your own fork of the repository.

1. Fork the `occupationcoder` repo on GitHub.
2. Clone your fork locally:
    ```
    $ git clone git@github.com:your_name_here/occupationcoder.git
    ```
3. Create a virtualenv for development. The following steps assume the use of the venv library:
    ```
    $ python3 -m venv occupationcoder
    ```

4. Create a branch for local development::
    ```
    $ git checkout -b name-of-your-bugfix-or-feature
    ```
   Now you can make your changes locally.

5. This repository makes use of pre-commit hooks. If approaching this project as a developer, you can install and enable pre-commit by running the following in your shell:

    ```
    $ pip install pre-commit
    $ pre-commit install
    ```

6. Commit your changes and push your branch to GitHub::
    ```
    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature
    ```
