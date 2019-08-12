# OntoLex-Lemon Validator

A Validator for OntoLex-Lemon Data

## Command Line Usage

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
