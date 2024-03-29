# Collecting Libraries Needed
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Data Import From CSV File

data = pd.read_csv('data.csv', encoding = 'utf-8')
kamus_abusive = pd.read_csv('abusive.csv', encoding = 'utf-8')
kamus_alay = pd.read_csv('new_kamusalay.csv', encoding = 'utf-8')

data