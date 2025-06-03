import React, { useRef, useState } from "react";

export const DocSearch = () => {
  const [document_folder, setdocument_folder] = useState("");
  const [error, setError] = useState(null);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  // Změň si endpoint na svůj skutečný Azure Function endpoint:
  const ENDPOINT_URL = "/api/search";

  const handleSubmit = async (e) => {
    e.preventDefault();
    const fileInput = fileInputRef.current;
    if (!fileInput.files.length) {
      setResponse("Vyberte soubor!");
      return;
    }
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    formData.append("document_folder", document_folder);

    setLoading(true);
    setResponse("Odesílám...");

    try {
      const res = await fetch(ENDPOINT_URL, {
        method: "POST",
        body: formData,
      });
      const datares = await res.json();
      setResponse(datares);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mt-5">
      <h2 className="mb-4">Nahrát dokument do Azure Function</h2>
      <form onSubmit={handleSubmit} className="mb-4">
        <div className="mb-3">
          <label htmlFor="fileInput" className="form-label">
            Dokument (PDF nebo DOCX):
          </label>
          <input
            type="file"
            className="form-control"
            id="fileInput"
            ref={fileInputRef}
            required
          />
        </div>
        <div className="mb-3">
          <label htmlFor="document_folder" className="form-label">
            URL dokumentu:
          </label>
          <input
            type="text"
            className="form-control"
            id="document_folder"
            value={document_folder}
            onChange={(e) => setdocument_folder(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? "Odesílám..." : "Odeslat"}
        </button>
      </form>
      <div className="alert alert-success">
        <pre>{JSON.stringify(response, null, 2)}</pre>
      </div>
      {error && <div className="alert alert-danger">
        <pre>{JSON.stringify(error, null, 2)}</pre>
      </div>}
    </div>
  );
}