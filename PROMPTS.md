# AI-Assisted Development Prompts

This document summarizes the main prompts and development steps used while extending the existing voice-transcription application.

## 1. Understand the Existing Project

**Prompt:**

Analyze the existing voice-transcription project and explain the current architecture, modules, data flow, API routes, frontend-backend interaction, Faster-Whisper integration, and LLM integration.

Identify which existing components can be reused while implementing the new functionality.

---

## 2. PDF Paragraph Extraction

**Prompt:**

Implement PDF paragraph extraction where the user can provide a PDF file, page number, and paragraph number.

The module should:

- Extract text from the selected page.
- Identify body paragraphs.
- Avoid treating headings as paragraphs where possible.
- Return the selected paragraph.
- Handle invalid page and paragraph numbers.
- Include unit tests.

---

## 3. Transcript Cleaning

**Prompt:**

Create a PDF text-cleaning module that reuses the existing TranscriptionService and LLM integration.

The extracted paragraph should be cleaned and normalized by:

- Fixing whitespace.
- Improving punctuation.
- Preserving the original meaning.
- Returning deterministic cleaned text where possible.

Treat the cleaned paragraph as the transcript for the next processing stages.

---

## 4. Topic and Subtopic Extraction

**Prompt:**

Using the cleaned transcript, extract the main topics and related subtopics.

Return the result as structured JSON.

Use Pydantic models to validate the response and handle invalid or malformed LLM output safely.

---

## 5. Hierarchy Generation

**Prompt:**

Convert the extracted topics and subtopics into a hierarchical tree structure.

Create a reusable hierarchy model with a root node and child nodes while preserving the topic and subtopic order.

---

## 6. Mermaid Mind-Map Generation

**Prompt:**

Generate a Mermaid mind-map definition from the hierarchical topic structure.

The output should:

- Have a root node.
- Display topics as child nodes.
- Display subtopics below their corresponding topics.
- Safely handle text that could interfere with Mermaid syntax.

---

## 7. HTML Visualization

**Prompt:**

Create an HTML renderer for the generated Mermaid mind map.

The generated HTML should load Mermaid and render the mind-map definition as a visual mind map that can be displayed in the application.

---

## 8. PDF Mind-Map Pipeline

**Prompt:**

Combine the individual modules into one PDF-to-mind-map pipeline.

The processing flow should be:

PDF
→ Page and paragraph selection
→ Paragraph extraction
→ Text cleaning
→ Topic/subtopic extraction
→ Hierarchy generation
→ Mermaid mind map
→ HTML visualization

Return the complete processing result in a structured response.

---

## 9. FastAPI Integration

**Prompt:**

Add a FastAPI endpoint:

POST /api/pdf-mindmap

The endpoint should accept:

- PDF file
- Page number
- Paragraph number

It should validate the request, temporarily store the uploaded PDF, execute the PDF mind-map pipeline, return the structured result, and clean up the temporary file.

---

## 10. React Frontend Integration

**Prompt:**

Extend the existing React frontend with a PDF mind-map interface.

Allow the user to:

- Upload a PDF.
- Enter a page number.
- Enter a paragraph number.
- Submit the document for processing.
- View the cleaned transcript.
- View extracted topics/subtopics.
- View the generated visual mind map.

Connect the interface to the /api/pdf-mindmap backend endpoint.

---

## 11. Testing and Error Handling

**Prompt:**

Add unit tests for the new PDF mind-map functionality.

Test:

- PDF paragraph extraction.
- Text cleaning.
- Topic extraction.
- Hierarchy generation.
- Mermaid generation.
- Pipeline behavior.
- Invalid inputs and error conditions.

Ensure the existing functionality continues to work.

---

## 12. Logging and Observability

**Prompt:**

Add logging for the PDF mind-map pipeline.

Capture useful processing information such as:

- Source metadata.
- Page and paragraph number.
- Text lengths.
- Processing duration.
- Topic/subtopic counts.
- Output sizes.
- Errors.
- Memory usage where available.

Do not fabricate unavailable token-usage information.

---

## 13. Documentation and Diagrams

**Prompt:**

Update the project documentation for the completed implementation.

Include:

- System architecture.
- Voice transcription flow.
- PDF-to-mind-map data flow.
- Data Flow Diagram (DFD).
- Component architecture.
- API sequence diagram.
- High-level system flow.
- Setup and usage instructions.
- Example workflow.

Use Mermaid for the architecture and flow diagrams.
