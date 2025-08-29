import os
import pandas as pd
import numpy as np
from biomni.tool.systems_biology import perform_flux_balance_analysis
from biomni.tool.literature import advanced_web_search
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Create output directory
output_dir = '/tmp/agent_outputs/2e8e073a-3e42-4114-bf6c-b59a99c37815'
os.makedirs(output_dir, exist_ok=True)

print("Step 1: Searching for iML1515 model information...")
search_results = advanced_web_search("iML1515 E. coli metabolic model SBML download", max_searches=3)
print("Search results:")
print(search_results)