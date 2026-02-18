import sys
import os
import json
from io import BytesIO

# Add project root to sys.path
sys.path.append(os.getcwd())

try:
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.pipeline import PIIPipeline
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

# Manually load pipeline to ensure it's available
print("Manually loading PIIPipeline...")
try:
    app.state.pii_pipeline = PIIPipeline()
    print("PIIPipeline loaded and attached to app.state.")
except Exception as e:
    print(f"Failed to load pipeline: {e}")
    sys.exit(1)

def test_csv_preview(client):
    print("\nTesting CSV Preview...")
    content = "name,email,phone\nJohn Doe,john@example.com,555-0100\nJane Smith,jane@example.com,555-0101"
    files = {'file': ('test.csv', content.encode('utf-8'), 'text/csv')}
    data = {'selected_columns': '["email", "phone"]'}
    
    try:
        response = client.post("/api/preview/csv", files=files, data=data)
        if response.status_code == 200:
            print("Success!")
            # Truncate output for readability if needed, but it's small
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_docx_preview(client):
    print("\nTesting DOCX Preview...")
    try:
        from docx import Document
        
        doc = Document()
        doc.add_paragraph("My name is John Doe and my email is john@example.com.")
        bio = BytesIO()
        doc.save(bio)
        bio.seek(0)
        
        files = {'file': ('test.docx', bio.read(), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
        data = {'selected_entities': '["EMAIL_ADDRESS", "PERSON"]'}
        
        response = client.post("/api/preview/docx", files=files, data=data)
        if response.status_code == 200:
            print("Success!")
            print(response.json())
        else:
            print(f"Failed: {response.status_code} - {response.text}")

    except ImportError:
        print("python-docx not installed, skipping.")
    except Exception as e:
        print(f"Error: {e}")

def test_pdf_preview(client):
    print("\nTesting PDF Preview...")
    try:
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "My name is John Doe and my email is john@example.com.")
        pdf_bytes = doc.tobytes()
        
        files = {'file': ('test.pdf', pdf_bytes, 'application/pdf')}
        data = {'selected_entities': '["EMAIL_ADDRESS"]'}
        
        response = client.post("/api/preview/pdf", files=files, data=data)
        if response.status_code == 200:
            print("Success!")
            print(response.json())
        else:
            print(f"Failed: {response.status_code} - {response.text}")
            
    except ImportError:
         print("fitz not installed, skipping.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    with TestClient(app) as client:
        test_csv_preview(client)
        test_docx_preview(client)
        test_pdf_preview(client)
