# First, let's search for information about iML1515 model and see if we can find it
from biomni.tool.literature import advanced_web_search
import os

# Create output directory
output_dir = '/tmp/agent_outputs/ca228c93-b36e-4b4d-96e4-6fc28f48ba2e'
os.makedirs(output_dir, exist_ok=True)

print("=== Searching for iML1515 model information ===")
search_results = advanced_web_search("iML1515 E. coli genome-scale metabolic model SBML download", max_searches=3)
print(search_results)