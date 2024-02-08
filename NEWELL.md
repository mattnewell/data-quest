* This assumes large-ish data, but not true big data.
  * HTTP-to-S3 uses chunked transfer encoding 
  * Assumes files up to gibibyte, maybe, but not multi-tibibyte.
  * A good fit for polars (faster than pandas), but without the complexity of spark.
* The README refers to the two datasets using multiple names. Could be cleaned up.
* I think the hint for trimming whitespace is a little much