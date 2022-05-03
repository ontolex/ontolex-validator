# OntoLex-Lemon Validator

A Validator for OntoLex-Lemon Data

## Command Line Usage

Install as in a virtual environment as follows:

    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt

You need to run the `source` command again each time you start the terminal.

You can validate a file simply by running

    python3 ontolex-validator.py file:/path/to/file.rdf
    
The command line options are

    -f [xml|turtle]    Change the format to parse the input as
    -o [txt|xml|html]  How to output the error list
    
## Web demo

There is a web demo that can be used at

http://server1.nlp.insight-centre.org/ontolex-validator/index.php

## Docker

A `Dockerfile` is provided to build the Web Server
