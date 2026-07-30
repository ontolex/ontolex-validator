# OntoLex-Lemon Validator

A Validator for OntoLex-Lemon Data

## Command Line Usage

Install in a virtual environment as follows:

    python -m venv env
    source env/bin/activate
    pip install -r requirements.txt

You need to run the `source` command again each time you start the terminal.

You can validate a file simply by running

    python3 ontolex-validator.py file:/path/to/file.rdf
    
The command line options are

    -f [xml|turtle]    Change the format to parse the input as
    -o [txt|xml|html]  How to output the error list
    
## SHACL shapes

`src/ontolex-shapes.ttl` is a SHACL translation of the checks performed
by `ontolex-validator.py`, so the same data can be validated with any
SHACL engine (e.g. [pySHACL](https://github.com/RDFLib/pySHACL)),
instead of running the python script. Validation results use
`sh:Violation`/`sh:Warning`/`sh:Info` severities matching the script's
errors/warnings/advisories, and each `sh:message` is prefixed with the
same rule code (e.g. `ENTRY_NO_CAN_FORM`) the script prints.

The file's header comment documents a handful of deliberate deviations
from the python script's actual (sometimes buggy) behaviour -- e.g.
`MULT_TYPES` and the dead `COMPONENT_NO_ELEM`/`COMPONENT_MANY_ELEM`/
`DP_INVALID_OBJ` checks are not reproduced, since they either have no
data-level meaning or can never fire in the original script.

Because pySHACL needs its "advanced" SPARQL-based shapes support for
several of these rules, validate with:

```python
from pyshacl import validate
conforms, results_graph, results_text = validate(
    "path/to/data.ttl",
    shacl_graph="src/ontolex-shapes.ttl",
    data_graph_format="turtle",
    shacl_graph_format="turtle",
    advanced=True,
)
print(results_text)
```

### Tests

`tests/compare.py` runs both `ontolex-validator.py` and the SHACL
shapes over every fixture in `tests/data/` and checks that they report
the same (rule code, severity) counts, to confirm the two stay in
sync:

    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt -r tests/requirements.txt
    .venv/bin/python3 tests/compare.py

## Web demo

There is a web demo that can be used at

http://server1.nlp.insight-centre.org/ontolex-validator/index.php

## Docker

A `Dockerfile` is provided to build the Web Server
