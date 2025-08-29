# Download the iML1515 model from BiGG Models database
import requests
import gzip
import os

print("=== Downloading iML1515 model from BiGG Models ===")

# Download the compressed SBML file
url = "http://bigg.ucsd.edu/static/models/iML1515.xml.gz"
model_compressed_path = os.path.join(output_dir, "iML1515.xml.gz")
model_path = os.path.join(output_dir, "iML1515.xml")

try:
    # Download the compressed file
    response = requests.get(url)
    response.raise_for_status()
    
    with open(model_compressed_path, 'wb') as f:
        f.write(response.content)
    
    print(f"Downloaded compressed model to: {model_compressed_path}")
    
    # Decompress the file
    with gzip.open(model_compressed_path, 'rb') as f_in:
        with open(model_path, 'wb') as f_out:
            f_out.write(f_in.read())
    
    print(f"Decompressed model saved to: {model_path}")
    print(f"Model file size: {os.path.getsize(model_path)} bytes")
    
except Exception as e:
    print(f"Error downloading model: {e}")