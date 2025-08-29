import urllib.request
import gzip
import cobra
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

print("Step 2: Downloading and loading iML1515 model...")

# Download the iML1515 model from BiGG database
model_url = "http://bigg.ucsd.edu/static/models/iML1515.xml.gz"
model_gz_path = os.path.join(output_dir, "iML1515.xml.gz")
model_path = os.path.join(output_dir, "iML1515.xml")

try:
    urllib.request.urlretrieve(model_url, model_gz_path)
    print(f"Downloaded model to: {model_gz_path}")
    
    # Extract the compressed file
    with gzip.open(model_gz_path, 'rb') as f_in:
        with open(model_path, 'wb') as f_out:
            f_out.write(f_in.read())
    
    print(f"Extracted model to: {model_path}")
    
    # Load the model using COBRApy
    model = cobra.io.read_sbml_model(model_path)
    print(f"\nModel loaded successfully!")
    print(f"Model ID: {model.id}")
    print(f"Number of reactions: {len(model.reactions)}")
    print(f"Number of metabolites: {len(model.metabolites)}")
    print(f"Number of genes: {len(model.genes)}")
    print(f"Objective function: {model.objective}")
    print(f"Objective direction: {model.objective.direction}")
    
    # Print some example reactions
    print(f"\nExample reactions:")
    for i, reaction in enumerate(model.reactions[:5]):
        print(f"{reaction.id}: {reaction.reaction}")
        
except Exception as e:
    print(f"Error: {e}")