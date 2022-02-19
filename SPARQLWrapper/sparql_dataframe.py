"""
Query a SPARQL endpoint and return results as a Pandas dataframe.
"""
import io
from typing import Any, Dict, List, Union

import rdflib.term

from SPARQLWrapper.SmartWrapper import Bindings, SPARQLWrapper2, Value
from SPARQLWrapper.Wrapper import CSV, SELECT, SPARQLWrapper


class QueryException(Exception):
    pass


def get_sparql_dataframe_orig(endpoint: str, query: Union[str, bytes]) -> Any: # -> pd.DataFrame:
    """copy paste from: https://github.com/lawlesst/sparql-dataframe"""
    # pandas inside to avoid requiring it
    import pandas as pd  # type: ignore[import]

    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    if sparql.queryType != SELECT:
        raise QueryException("Only SPARQL SELECT queries are supported.")
    sparql.setReturnFormat(CSV)
    results = sparql.query().convert()
    if isinstance(results, bytes):
        _csv = io.StringIO(results.decode("utf-8"))
        return pd.read_csv(_csv, sep=",")
    else:
        raise TypeError(type(results))


def get_sparql_typed_dict(
    endpoint: str, query: Union[str, bytes]
) -> List[Dict[str, Value]]:
    """modified from: https://github.com/lawlesst/sparql-dataframe"""
    # pandas inside to avoid requiring it
    import pandas as pd

    sparql = SPARQLWrapper2(endpoint)
    sparql.setQuery(query)
    if sparql.queryType != SELECT:
        raise QueryException("Only SPARQL SELECT queries are supported.")
    # sparql.setReturnFormat(JSON)
    results = sparql.query()
    if not isinstance(results, Bindings):
        raise TypeError(type(results))
    # consider perf hacking later, probably slow
    # convert list of dicts to python types
    d = []
    for x in results.bindings:
        row = {}
        for k in x:
            v = x[k]
            vv = rdflib.term.Literal(v.value, datatype=v.datatype).toPython()  # type: ignore[no-untyped-call]
            row[k] = vv
        d.append(row)
    return d


def get_sparql_dataframe(endpoint: str, query: Union[str, bytes]) -> Any: # -> pd.DataFrame:
    # pandas inside to avoid requiring it
    import pandas as pd

    d = get_sparql_typed_dict(endpoint, query)
    # TODO: will nan fill somehow, make more strict if there is way of getting the nan types from rdflib
    df = pd.DataFrame(d)
    return df
