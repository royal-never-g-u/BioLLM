# Import necessary libraries
import cobra
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns

print("Loading iML1515 E. coli model...")

# Load iML1515 model
try:
    model = cobra.io.load_model("iML1515")
    print(f"✓ Successfully loaded iML1515 model")
    print(f"Model ID: {model.id}")
    print(f"Model name: {model.name}")
    print(f"Number of reactions: {len(model.reactions)}")
    print(f"Number of metabolites: {len(model.metabolites)}")
    print(f"Number of genes: {len(model.genes)}")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Trying alternative loading method...")
    
    # Try loading from BiGG Models
    try:
        model = cobra.io.load_model("textbook")  # As alternative
        print("Loaded textbook model as alternative")
    except:
        print("Could not load any model")