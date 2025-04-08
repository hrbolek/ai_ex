import { useState } from 'react';
import './App.css';

interface SearchResult {
  id: number;
  url: string;
  score: number;
}
function App() {
  const [searchText, setSearchText] = useState('');
  const [results, setResults] = useState<Array<SearchResult>>([]);
  const [isLoading, setIsLoading] = useState(false);

  const signature = "?sv=2024-11-04&ss=bf&srt=co&sp=rx&se=2026-04-08T19:35:57Z&st=2025-04-08T11:35:57Z&spr=https&sig=Bl7RxF73HhCad2OBVXEcSQpEdIDPhwlfpfEBgIjedZo%3D"
  const blobStorageUrl = "https://stsemanticindex.blob.core.windows.net/data/"

  async function search() {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/search?query=${encodeURIComponent(searchText)}`);
      const data = await response.json();
      setResults(data); // Update results state with fetched data
    } catch (error) {
      console.error('Error fetching search results:', error);
    } finally {
      setIsLoading(false);
    }
  }



  return (
    <div className="App">
      <header className="App-header">
        {isLoading ? <div>Načítám</div> : <> <input
          type="text"
          placeholder="Co chcete vyhledat?"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
          <button onClick={search}>Vyhledat</button>
        </>}
        {results.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Id</th>
                <th>Url</th>
                <th>Skóre</th>
              </tr>
            </thead>
            <tbody>
              {results.map((item, index) => (
                <tr key={index}>
                  <td>{item.id}</td>
                  <td><a href={`${blobStorageUrl}${item.url}${signature}`} target="_blank" rel="noopener noreferrer">{item.url}</a></td>
                  <td>{item.score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </header>
    </div>
  );
}

export default App;
