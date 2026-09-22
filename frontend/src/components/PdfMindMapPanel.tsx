import { FileText, LoaderCircle, Sparkles } from 'lucide-react';
import { useState } from 'react';
import styles from './PdfMindMapPanel.module.css';
import { Box } from './Box';
import type { PdfMindMapResponse } from '../types';

export function PdfMindMapPanel() {
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [pageNumber, setPageNumber] = useState('1');
  const [paragraphNumber, setParagraphNumber] = useState('1');
  const [result, setResult] = useState<PdfMindMapResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async () => {
    const page = Number(pageNumber);
    const paragraph = Number(paragraphNumber);

    if (!pdfFile) {
      setError('Select a PDF file first.');
      return;
    }
    if (!Number.isInteger(page) || page < 1) {
      setError('Page number must be a whole number greater than zero.');
      return;
    }
    if (!Number.isInteger(paragraph) || paragraph < 1) {
      setError('Paragraph number must be a whole number greater than zero.');
      return;
    }

    const formData = new FormData();
    formData.append('file', pdfFile);
    formData.append('page_number', String(page));
    formData.append('paragraph_number', String(paragraph));

    setError(null);
    setResult(null);
    setIsProcessing(true);

    try {
      const response = await fetch('/api/pdf-mindmap', {
        method: 'POST',
        body: formData,
      });

      const data = (await response.json()) as
        | PdfMindMapResponse
        | { detail?: string };

      if (!response.ok) {
        throw new Error(
          'detail' in data && data.detail
            ? data.detail
            : 'PDF mind-map generation failed.'
        );
      }

      setResult(data as PdfMindMapResponse);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : 'PDF mind-map generation failed.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <section className={styles.container} aria-labelledby="pdf-mind-map-title">
      <Box header="PDF Mind Map" icon={FileText}>
        <p className={styles.intro} id="pdf-mind-map-title">
          Select a body paragraph from a PDF and turn it into a visual mind map.
        </p>

        <div className={styles.controls}>
          <label className={styles.fileField}>
            <span>PDF file</span>
            <input
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) => setPdfFile(event.target.files?.[0] || null)}
            />
            <strong>{pdfFile?.name || 'Choose a PDF'}</strong>
          </label>

          <label>
            <span>Page</span>
            <input
              type="number"
              min="1"
              value={pageNumber}
              onChange={(event) => setPageNumber(event.target.value)}
            />
          </label>

          <label>
            <span>Paragraph</span>
            <input
              type="number"
              min="1"
              value={paragraphNumber}
              onChange={(event) => setParagraphNumber(event.target.value)}
            />
          </label>
        </div>

        <button
          className={styles.submitButton}
          type="button"
          onClick={() => void handleSubmit()}
          disabled={isProcessing}
        >
          {isProcessing ? (
            <LoaderCircle className={styles.buttonIcon} aria-hidden="true" />
          ) : (
            <Sparkles className={styles.buttonIcon} aria-hidden="true" />
          )}
          {isProcessing ? 'Generating...' : 'Generate Mind Map'}
        </button>

        {error && <p className={styles.error} role="alert">{error}</p>}

        {result && (
          <div className={styles.results}>
            <div className={styles.meta}>
              <strong>{result.source_pdf}</strong>
              <span>
                Page {result.page_number}, paragraph {result.paragraph_number}
              </span>
              <span>{result.processing_time_ms.toFixed(1)} ms</span>
            </div>

            <div className={styles.textGrid}>
              <div>
                <h4>Extracted paragraph</h4>
                <p>{result.extracted_text}</p>
              </div>
              <div>
                <h4>Cleaned paragraph</h4>
                <p>{result.cleaned_text}</p>
              </div>
            </div>

            <div>
              <h4>Topics</h4>
              {result.topics.topics.length > 0 ? (
                <ul className={styles.topicList}>
                  {result.topics.topics.map((topic) => (
                    <li key={topic.name}>
                      <strong>{topic.name}</strong>
                      {topic.subtopics.length > 0 && (
                        <ul>
                          {topic.subtopics.map((subtopic) => (
                            <li key={subtopic}>{subtopic}</li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className={styles.muted}>No topics were extracted.</p>
              )}
            </div>

            <div>
              <h4>Visual mind map</h4>
              <iframe
                className={styles.preview}
                title="Generated PDF mind map"
                srcDoc={result.html}
                sandbox="allow-scripts allow-same-origin"
              />
            </div>
          </div>
        )}
      </Box>
    </section>
  );
}