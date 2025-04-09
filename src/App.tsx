import { useState } from 'react';
import { PrimeReactProvider } from 'primereact/api';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import './App.css';
import "primereact/resources/themes/lara-light-cyan/theme.css";
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';

interface SearchResult {
  id: number;
  url: string;
  score: number;
  content: string;
}

function App() {
  const [searchText, setSearchText] = useState('');
  const [results, setResults] = useState<Array<SearchResult>>([]);
  const [isLoading, setIsLoading] = useState(false);

  let blobStorageUrl = process.env.REACT_APP_BLOB_STORAGE_URL || '';
  let signature = process.env.REACT_APP_BLOB_ACCESS_SIGNATURE || '';
  

  async function search() {
    setIsLoading(true);
    setResults([]); 
    try {
      const response = await fetch(`/api/search?query=${encodeURIComponent(searchText)}`);
      const data = await response.json();
      setResults(data); 
    } catch (error) {
      console.error('Error fetching search results:', error);
    } finally {
      setIsLoading(false);
    }
  }

  const urlBodyTemplate = (result: SearchResult) => {
    return <a
      href={`${blobStorageUrl}${result.url}${signature}`}
      target="_blank"
      rel="noopener noreferrer"
    >
      {result.url}
    </a>

  };

  return (
    <PrimeReactProvider>
      <div className="App">        
        <h2 className="text-2xl font-bold mb-4">Vyhledávání v dokumentech</h2>
        <div className="flex flex-wrap justify-content-center gap-2 mb-4 mt-4">
          {isLoading ? <div>Načítám</div> : <> <InputText
            type="text"
            placeholder="Co chcete vyhledat?"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onKeyUp={(e => {
              if (e.key === 'Enter') {
                search();
              }
            })}
          />
            <Button label="Vyhledat" icon="ml-4" onClick={search} />
          </>}
        </div>
        {results.length > 0 && (<>
          <DataTable value={results} tableStyle={{ minWidth: '50rem' }}>
            <Column field="url" header="Url" body={urlBodyTemplate} >
            </Column>
            <Column field="content" header="Obsah"></Column>
          </DataTable>
        </>)}

      </div>
    </PrimeReactProvider>
  );
}

export default App;
