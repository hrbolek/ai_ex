import { useEffect, useState } from 'react';
import './App.css';

const DocumentsDisplay = ({data}) => {
// Handle case where data is null/undefined or documents doesn't exist
  if (!data || !data.documents || !Array.isArray(data.documents)) {
    return <div className="p-4 text-gray-500">No documents found</div>;
  }
  const sortedDocs = data?.documents?.sort((a, b) => b.score - a.score) || []
return (
    <div className="p-6 max-w-4xl mx-auto">
      
      <p className="text-gray-600 text-base">({data.summary})</p>
      <p className="text-2xl font-bold mb-4">Počet dokumentů ({data.documents.length})</p>
      <ul>
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
      </ul>
    </div>
  );
};

export const SearchApp = () => {
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
            {isLoading ? <div>Načítám</div> : <>
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
            </>}
          </div>
        </div>
        {/*<pre>{JSON.stringify(result, null, 2)}</pre>*/}
         {result && <DocumentsDisplay data={result} />}
      </div>
    
  );
  
};



