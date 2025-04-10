import { useEffect, useState } from 'react';
import { PrimeReactProvider } from 'primereact/api';
import { Button } from 'primereact/button';
import { InputText } from 'primereact/inputtext';
import './App.css';
import 'primeflex/primeflex.css';
import "primereact/resources/themes/lara-light-cyan/theme.css";
import { DataTable } from 'primereact/datatable';
import { Column } from 'primereact/column';
import userEvent from '@testing-library/user-event';

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
  const [requestCount, setRequestCount] = useState<number>(0)
  const [quota, setQuota] = useState<number>(0)
  const [quotaExceeded, setQuotaExceeded] = useState(false)

  let blobStorageUrl = process.env.REACT_APP_BLOB_STORAGE_URL || '';
  let signature = process.env.REACT_APP_BLOB_ACCESS_SIGNATURE || '';


  async function search() {
    if (searchText.length === 0) {
      return;
    }
    setIsLoading(true);
    setResults([]);
    try {
      const response = await fetch(`/api/search?query=${encodeURIComponent(searchText)}`);
      const data = await response.json();
      setResults(data);
      setRequestCount(requestCount! + 1);
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

  useEffect(() => {
    setQuotaExceeded(requestCount >= quota)
  }, [requestCount, quota])

  useEffect(() => {
    const fetchQuota = async () => {
      try {
        const response = await fetch('/api/quota');
        const data = await response.json();
        setRequestCount(data.requestCount);
        setQuota(data.quota);
        console.log('Quota information:', data);
      } catch (error) {
        console.error('Error fetching quota information:', error);
      }
    };

    fetchQuota();
  }, []);

  return (
    <PrimeReactProvider>
      <div className="App">
        <h2 className="text-2xl font-bold mb-4">Vyhledávání v dokumentech</h2>
        <div className="flex flex-column align-items-center">
          <div className="flex flex-wrap justify-content-center gap-2 mb-4 mt-4" style={{ maxWidth: '500px' }}>
            {isLoading ? <div>Načítám</div> : <>
              <div className="p-inputgroup flex-1">
                <span className="p-inputgroup-addon">{requestCount}/{quota}</span>
                 <InputText
                  disabled={quotaExceeded}
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

                <Button disabled={quotaExceeded || searchText.length === 0} label="Vyhledat" icon="ml-4" onClick={search} />
              </div>
            </>}
          </div>
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
