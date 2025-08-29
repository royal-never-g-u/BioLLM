import urllib.request
import gzip
import cobra
print("Step 2: Downloading iML1515 model...")

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
    
    # Load the model using COBRApy to examine its structure
    model = cobra.io.read_sbml_model(model_path)
    print(f"\nModel loaded successfully!")
    print(f"Model ID: {model.id}")
    print(f"Number of reactions: {len(model.reactions)}")
    print(f"Number of metabolites: {len(model.metabolites)}")
    print(f"Number of genes: {len(model.genes)}")
    print(f"Objective function: {model.objective}")
    
except Exception as e:
    print(f"Error downloading/loading model: {e}")
    # Alternative: try direct download without compression
    try:
        model_url_alt = "http://bigg.ucsd.edu/static/models/iML1515.xml"
        urllib.request.urlretrieve(model_url_alt, model_path)
        print(f"Downloaded uncompressed model to: {model_path}")
        model = cobra.io.read_sbml_model(model_path)
        print(f"Model loaded successfully via alternative method!")
        print(f"Model ID: {model.id}")
        print(f"Number of reactions: {len(model.reactions)}")
        print(f"Number of metabolites: {len(model.metabolites)}")
        print(f"Number of genes: {len(model.genes)}")
        print(f"Objective function: {model.objective}")
    except Exception as e2:
        print(f"Alternative download also failed: {e2}")