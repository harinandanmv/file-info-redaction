from docx import Document
from io import BytesIO

def redact_docx_paragraphwise(
    original_doc_bytes: bytes,
    pipeline,
    selected_entities: list[str] | None
) -> tuple[BytesIO, int]:
    doc = Document(BytesIO(original_doc_bytes))
    total_entity_count = 0

    for para in doc.paragraphs:
        # 1. Build full text from runs to preserve formatting during reconstruction
        full_text = "".join([run.text for run in para.runs])

        if not full_text:
            continue

        # 2. Run detection on full text
        _, entities = pipeline.run(full_text)
        
        # 3. Create a mask for characters to be redacted
        # chars_to_redact[i] == True means the character at index i should be '*'
        chars_to_redact = [False] * len(full_text)
        
        for e in entities:
            if selected_entities is not None and e.entity_type not in selected_entities:
                continue

            if e.start < 0 or e.end > len(full_text):
                 continue
                 
            # Heuristic: Avoid redaction if the entity consumes too much of the paragraph, 
            # likely a false positive, UNLESS the text is short enough to be a title/header.
            span_len = e.end - e.start
            if span_len > 60 or (len(full_text) > 50 and span_len / len(full_text) > 0.8):
                 continue

            # Count this entity as it will be redacted
            total_entity_count += 1

            for i in range(e.start, e.end):
                chars_to_redact[i] = True

        # 4. Apply redaction mask to runs
        # Reconstruct each run's text by pulling strictly from the original text (preserved in run.text)
        # or replacing with '*', based on the global index we track.
        current_global_idx = 0
        for run in para.runs:
            run_chars = list(run.text)
            for i in range(len(run_chars)):
                if current_global_idx < len(chars_to_redact) and chars_to_redact[current_global_idx]:
                    run_chars[i] = "*"
                current_global_idx += 1
            run.text = "".join(run_chars)

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output, total_entity_count
