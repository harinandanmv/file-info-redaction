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
        words = page.get_text("words")
        if not words:
            continue
            
        full_text = ""
        word_map = [] 
        
        current_idx = 0
        for w in words:
            word_str = w[4]
            rect = fitz.Rect(w[0], w[1], w[2], w[3])
            
            start = current_idx
            end = start + len(word_str)
            word_map.append((start, end, rect))
            
            full_text += word_str + " " 
            current_idx = end + 1

        if not full_text.strip():
            continue
            
        _, entities = pipeline.run(full_text)
        
        for e in entities:
            if selected_entities is None or e.entity_type in selected_entities:
                total_entity_count += 1
        
        for e in entities:
            if selected_entities is not None and e.entity_type not in selected_entities:
                continue
            
            for w_start, w_end, w_rect in word_map:
                overlap_start = max(e.start, w_start)
                overlap_end = min(e.end, w_end)
                
                if overlap_start < overlap_end:
                    intersection_len = overlap_end - overlap_start
                    word_len = w_end - w_start
                    
                    if word_len > 0:
                        ratio = intersection_len / word_len
                        
                        if ratio >= 0.5:
                             page.add_redact_annot(
                                 w_rect, 
                                 text="*"*len(full_text[w_start:w_end]), 
                                 fill=(1, 1, 1), 
                                 text_color=(0, 0, 0),
                                 fontsize=10
                             )
        
        page.apply_redactions()
        
    pdf_bytes = doc.tobytes(garbage=4, deflate=True)
    return BytesIO(pdf_bytes), total_entity_count
