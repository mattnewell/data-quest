# TODO: Jupyter Notebook, and maybe the other Jetbrains product?
# TODO: Pull into SQL database to double check the data?
import s3fs
import polars as pl
import os
import json


s3 = s3fs.S3FileSystem()
productivity_schema = {
    "series_id": pl.Utf8,
    "year": pl.Int64,
    "period": pl.Utf8,
    "value": pl.Float64,
    "footnote_codes": pl.Utf8
}
productivity_df = pl.read_csv("s3://newell-data-quest/pr.data.0.Current", separator='\t',
                              schema=productivity_schema).with_columns(pl.col(pl.Utf8).str.strip_chars())
print(productivity_df)
population_json = json.loads(s3.open('s3://newell-data-quest/datausa_nation_pop.json').read())['data']
population_df = pl.DataFrame(population_json)
print(population_df)
selected_years_df = population_df.filter(
    pl.col('ID Year') >= 2013,
    pl.col('ID Year') <= 2018
).select('Population')
print(selected_years_df.mean())
print(selected_years_df.std())

q = (
    productivity_df
    .group_by('series_id', 'year')
    .agg([
        pl.sum('value').alias('total_value'),
    ])
    .sort('series_id', 'total_value', descending=[False, True])
    .group_by('series_id')
    .first()
)
print(q)

prod_pop = (population_df
            .join(productivity_df, left_on='ID Year', right_on='year', how='inner')
            .filter(
                pl.col('series_id') == 'PRS30006032',
                pl.col('period') == 'Q01'
            )
            .select('series_id', 'ID Year', 'period', 'value', 'Population'))
print(prod_pop)
