import json

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T


from IPython.display import JSON
from IPython.core.display_functions import display

import spark_utils

SPARK = spark_utils.spark_context()

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalTrueColorFormatter

def ppd(d, indent=2):
    'pretty-prints a dict'
    print(highlight(
        code      = json.dumps(d, indent=indent),
        lexer     = JsonLexer(),
        formatter = TerminalTrueColorFormatter(style='material')
    ).strip())
def ppj(j, indent=2):
    'pretty-prints a JSON string'
    ppd(json.loads(j), indent=indent)


def count_nulls(df: DataFrame) -> int:
    return df.select(
        sum([F.count(F.when(F.col(c).isNull(), c)) for c in df.columns])
    ).collect()[0][0]

def count_cells(df: DataFrame) -> int:
    return df.count() * len(df.columns)

class DFLoader:
    @staticmethod
    def from_file(records: list, fpath: str = 'f.ndjson', schema: dict = {}) -> DataFrame:
        with open(fpath, 'w') as ostream:
            for record in records:
                print(json.dumps(record), file=ostream, end='\n')
        if schema:
            df = SPARK.read.json(fpath, schema=T.StructType.fromJson(schema))
        else:
            df = SPARK.read.json(fpath)
        # df.show()
        display(df.toPandas())
        # display(df.toPandas())
        print('cells', count_cells(df), '/', 'nulls', count_nulls(df))
        ppj(df.schema.json())
        # display(JSON(json.loads(df.schema.json()), expanded=True))
        return df
