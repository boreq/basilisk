# Basilisk
Basilisk is a static website generator which builds HTML websites from a set of
static files in multiple formats such as HTML, markdown or plain text.

# Setup
In order to install the package from this repository and confirm that the
installation was successful execute the following commands:

    pip install git+https://github.com/boreq/basilisk
    basilisk --help

# Usage
To build the example execute the following command:

    $ basilisk build examples/basic output

You can also use the development server:

    $ basilisk serve examples/basic
