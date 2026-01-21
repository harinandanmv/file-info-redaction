import fitz  # PyMuPDF
from io import BytesIO

def redact_pdf_file(
    file_bytes: bytes,
    pipeline,
    selected_entities: list[str] | None
) -> tuple[BytesIO, int]:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    total_entity_count = 0
    
    for page in doc:
        # 1. Extract words with coordinates
        # words is a list of (x0, y0, x1, y1, "word", block_no, line_no, word_no)
        words = page.get_text("words")
        if not words:
            continue
            
        # 2. Reconstruct text and build strict mapping
        # We join words with spaces to create a linear text for the detector
        # We map the character range of each word in 'full_text' back to its PDF rectangle
        full_text = ""
        word_map = [] # List of (start_index, end_index, rect)
        
        current_idx = 0
        for w in words:
            word_str = w[4]
            rect = fitz.Rect(w[0], w[1], w[2], w[3])
            
            # Map this word's characters in the full buffer
            start = current_idx
            end = start + len(word_str)
            word_map.append((start, end, rect))
            
            full_text += word_str + " " # Add space for reconstruction
            current_idx = end + 1

        if not full_text.strip():
            continue
            
        # 3. Run detection on reconstruction
        _, entities = pipeline.run(full_text)
        
        # 4. Count entities that will be redacted
        for e in entities:
            if selected_entities is None or e.entity_type in selected_entities:
                total_entity_count += 1
        
        # 5. Locate and redact entities based on indices
        for e in entities:
            if selected_entities is not None and e.entity_type not in selected_entities:
                continue
                
            # Find any words that intersect with the entity's character range
            # e.start / e.end refer to full_text
            
            for w_start, w_end, w_rect in word_map:
                # Check for overlap
                # Overlap logic: max(start1, start2) < min(end1, end2)
                overlap_start = max(e.start, w_start)
                overlap_end = min(e.end, w_end)
                
                if overlap_start < overlap_end:
                    intersection_len = overlap_end - overlap_start
                    word_len = w_end - w_start
                    
                    if word_len > 0:
                        # Debug logging
                        print(f"DEBUG: Checking '{full_text[w_start:w_end]}' vs Entity '{full_text[e.start:e.end]}' ({e.entity_type})")
                        
                        # Simple Ratio logic:
                        # If the intersection covers the majority of the word (> 75%), redact it.
                        ratio = intersection_len / word_len
                        print(f"DEBUG: Intersection: {intersection_len}, WordLen: {word_len}, Ratio: {ratio:.2f}")
                        
                        if ratio > 0.75:
                             print(f"DEBUG: REDACTING '{full_text[w_start:w_end]}'")
                             page.add_redact_annot(
                                 w_rect, 
                                 text="*"*len(full_text[w_start:w_end]), 
                                 fill=(1, 1, 1), 
                                 text_color=(0, 0, 0),
                                 fontsize=10
                             )
        
        # 6. Apply all redactions for this page
        page.apply_redactions()
        
    # Use tobytes() to get the PDF content safely
    # garbage=4: Remove unused objects (cleaned up)
    # deflate=True: Compress streams
    pdf_bytes = doc.tobytes(garbage=4, deflate=True)
    return BytesIO(pdf_bytes), total_entity_count
