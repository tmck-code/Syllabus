from pyspark.sql import SparkSession

def spark_context():
    'Creates a local spark context'
    return (
        SparkSession.builder
        .master('local')
        .appName('syllabus')
        .getOrCreate()
    )