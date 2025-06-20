HTML="""<!DOCTYPE html>
<html lang="en">
<head>
  <title>Bootstrap 5 & ReactJS Example</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>

  <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
  <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>  

  <script src="https://unpkg.com/babel-standalone@6/babel.min.js"></script>
  <script src="https://unpkg.com/htm@2.2.1" crossorigin></script>

  <script src="https://unpkg.com/@reduxjs/toolkit@1.9.3/dist/redux-toolkit.umd.js"></script>
  <script src="https://unpkg.com/react-markdown@7.0.1/react-markdown.min.js"></script>
</head>

<body>

    <div class="container-fluid p-5 bg-primary text-white text-center">
        <h1>Sémantické vyhledávání</h1>
    </div>
    
    <div class="container mt-5">
        <div id="root"></div>
    </div>


    <script  type="module">
      // import * as all from "https://unpkg.com/react-markdown@7.0.1/react-markdown.min.js";
      // console.log(all.ReactMarkdown)
      // console.log(all)
      // console.log(Object.keys(all))
      // console.log("ReactMarkdown")
      // console.log(ReactMarkdown)
      // let Markdown = ReactMarkdown.default
      // console.log("Markdown")
      // console.log(Markdown)
    </script>
    <script type="text/babel">
        
        const { useState, useRef, useEffect } = React;
        const { configureStore, createSlice } = RTK;
        console.log("React", JSON.stringify(React))
        
        let Markdown = ReactMarkdown.default

const DocumentsDisplay = ({data}) => {
// Handle case where data is null/undefined or documents doesn't exist
  if (!data || !data.documents || !Array.isArray(data.documents)) {
    return <div className="p-4 text-gray-500">No documents found</div>;
  }
  const docs = data.documents || []
  const sortedDocs = docs.sort((a, b) => b.score - a.score) || []
return (
    <div className="p-6 max-w-4xl mx-auto">
      <Markdown>{data.summary}</Markdown>
      {false && <div>
      <p className="text-gray-600 text-base">
        ({data.summary})</p>
      <p className="text-2xl font-bold mb-4">Počet dokumentů ({data.documents.length})</p>
      </div>}
      {false && <ul>
        {sortedDocs.map((document, index) => (
          <li key={index}>
            <a 
              href={document.document_folder}
              className="text-blue-600 hover:text-blue-800 hover:underline mr-2"
            >
              {document.document_folder}
            </a>

            <span className="text-gray-600">({document.score} skóre)</span>
          </li>
        ))}
      </ul>}
    </div>
  );
};

const PremyslimDots = () => {
  const [dots, setDots] = useState("");
  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => (prev.length < 3 ? prev + "." : ""));
    }, 400);
    return () => clearInterval(interval);
  }, []);
  return (
    <div style={{ fontSize: "2rem", fontWeight: "bold", color: "#007bff" }}>
      Přemýšlím{dots}
    </div>
  );
}

const SearchApp = () => {
  const [searchText, setSearchText] = useState("");
  const [result, setResult] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [requestCount, setRequestCount] = useState(null)

  async function search() {
    if (searchText.length === 0) {
      return;
    }
    setIsLoading(true);
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(searchText)}`);
      //const response = await fetch(`/api/search?q=${encodeURIComponent(searchText)}`);
      const data = await response.json();
      setResult(data);
      setRequestCount(requestCount + 1);
    } catch (error) {
      console.error('Error fetching search results:', error);
      setResult(error);
    } finally {
      setIsLoading(false);
    }
  }
  
  return (
    
      <div className="SearchApp">
        <h2 className="text-2xl font-bold mb-4">Vyhledávání v dokumentech</h2>
        <div className="flex flex-column align-items-center">
          <div >
            <Markdown>Hello</Markdown>
            <div >
                <input
                  type="text"
                  className="form-control"
                  placeholder="Co chcete vyhledat?"
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  onKeyUp={(e => {
                    if (e.key === 'Enter') {
                      search();
                    }
                  })}
                  />

                <button className='btn btn-outline-success' disabled={searchText.length === 0} label="Vyhledat" onClick={search} >Vyhledat</button>
              </div>
            {isLoading && <PremyslimDots />}
          </div>
        </div>
        {/*<pre>{JSON.stringify(result, null, 2)}</pre>*/}
         {result && <DocumentsDisplay data={result} />}
      </div>
    
  );
  
};


const DocAdd = () => {
  const [document_folder, setdocument_folder] = useState("");
  const [error, setError] = useState(null);
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);

  // Změň si endpoint na svůj skutečný Azure Function endpoint:
  const ENDPOINT_URL = "/api/adddocument";

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
        

const App = () => {
  const [app, setApp] = useState(0)
  const handleClick = (value) => () => setApp(value)
  return (
    <div className="container mt-5">
      {app == 1 && <button className="btn btn-outline-primary form-control" onClick={handleClick(0)}>Search</button>}
      {app == 0 && <button className="btn btn-outline-primary form-control" onClick={handleClick(1)}>Přidávat dokumenty</button>}
      {app == 1 && <DocAdd />}
      {app == 0 && <SearchApp />}
    </div>
  );
};


const container = document.getElementById('root');
        const root = ReactDOM.createRoot(container);
        root.render(<App />);

    </script>

</body>
</html>
"""