# This program was made by:
#
# Nilo Martins and Ricardo Paranhos
#
# to a class of Computer Intelligence
#
# by Prof. Fernando Buarque, PhD
#
# from University of Pernambuco – UPE,
# School of Engineering – POLI
#
# Year 2018
#
# This software are licensed by GPLv3
#
# Contact: jniloms@gmail.com

import numpy as np
import pandas as pd

# Split dataset in 80% to training and 20% to test
def splitdataset(df):
  msk = np.random.rand(len(df)) < 0.8
  training = df[msk]
  test = df[~msk]
  return training, test


# Load CSV in dataset ignoring not numéric values
def loaddataset(filename, sep=';'):

    df = pd.read_csv(filename, sep=sep)
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.dropna(axis=1)
    return df