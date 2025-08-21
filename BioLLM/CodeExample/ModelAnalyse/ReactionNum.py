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
    print(f"Error loading iML1515: {e}")
    print("Trying to load from BiGG Models...")
    
    # Try loading from URL
    try:
        model = cobra.io.load_json_model("http://bigg.ucsd.edu/static/models/iML1515.json")
        print(f"✓ Successfully loaded iML1515 from BiGG Models")
        print(f"Model ID: {model.id}")
        print(f"Model name: {model.name}")
        print(f"Number of reactions: {len(model.reactions)}")
        print(f"Number of metabolites: {len(model.metabolites)}")
        print(f"Number of genes: {len(model.genes)}")
    except Exception as e2:
        print(f"Error loading from URL: {e2}")
        # Use built-in E. coli core model as example
        model = cobra.test.create_test_model("ecoli")
        print(f"Using E. coli core model as example:")
        print(f"Number of reactions: {len(model.reactions)}")
        print(f"Number of metabolites: {len(model.metabolites)}")
        print(f"Number of genes: {len(model.genes)}")