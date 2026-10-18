#generates the data frame with bibio info.
import pandas as pd
from functions_and_classes.cloud_io import df_from_gc_csv

dl_files = df_from_gc_csv('List-of-Works.csv')
