# Load and examine the iML1515 model using COBRApy
import cobra
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("=== Loading and examining iML1515 model ===")

# Load the model
model = cobra.io.read_sbml_model(model_path)

print(f"Model name: {model.name}")
print(f"Model ID: {model.id}")
print(f"Number of reactions: {len(model.reactions)}")
print(f"Number of metabolites: {len(model.metabolites)}")
print(f"Number of genes: {len(model.genes)}")

# Get model compartments
compartments = {}
for compartment in model.compartments:
    compartments[compartment] = model.compartments[compartment]

print(f"\nCompartments:")
for comp_id, comp_name in compartments.items():
    print(f"  {comp_id}: {comp_name}")

# Check objective function
print(f"\nObjective function: {model.objective}")
print(f"Objective direction: {model.objective.direction}")

# Get some basic statistics about reactions
exchange_reactions = [r for r in model.reactions if r.id.startswith('EX_')]
transport_reactions = [r for r in model.reactions if any(keyword in r.name.lower() for keyword in ['transport', 'transporter', 'symporter', 'antiporter']) if hasattr(r, 'name') and r.name]

print(f"\nReaction categories:")
print(f"  Exchange reactions: {len(exchange_reactions)}")
print(f"  Transport reactions: {len(transport_reactions)}")
print(f"  Internal reactions: {len(model.reactions) - len(exchange_reactions)}")

# Update plan
print("\n✓ Step 1: Model loading completed")
print("✓ Step 2: Model structure examination completed")