
import sys
import os
# Add the current directory to sys.path so we can import app modules
sys.path.append(os.getcwd())

from app.core.pipeline import PIIPipeline
from app.utils.pdf_redactor import redact_pdf_file
import fitz

def test_on_file(filename):
    print(f"Loading pipeline...")
    pipeline = PIIPipeline()
    
    print(f"Reading {filename}...")
    with open(filename, "rb") as f:
        file_bytes = f.read()
    
    print(f"Running redaction...")
    # Run the utility
    redacted_io = redact_pdf_file(
        file_bytes=file_bytes,
        pipeline=pipeline,
        selected_entities=None # Redact all detected
    )
    
    output_filename = f"redacted_{filename}"
    print(f"Saving to {output_filename}...")
    with open(output_filename, "wb") as f_out:
        f_out.write(redacted_io.getvalue())
        
    print("Done!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = "devikaresfinal.pdf"
        
    if not os.path.exists(fname):
        print(f"File {fname} not found!")
    else:
        test_on_file(fname)
