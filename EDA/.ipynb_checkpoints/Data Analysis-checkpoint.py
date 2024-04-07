# Collecting Libraries Needed
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Data Import From CSV File

data = pd.read_csv('data.csv')
kamus_abusive = pd.read_csv('abusive.csv')
kamus_alay = pd.read_csv('new_kamusalay.csv')

data