import pandas as pd
from functions_and_classes.cloud_io import df_from_gc_csv

awprev_df = df_from_gc_csv('awpreverse.csv')
awcrev_df = df_from_gc_csv('awcreverse.csv')
swprev_df = df_from_gc_csv('swpreverse.csv')
swcrev_df = df_from_gc_csv('swcreverse.csv')
