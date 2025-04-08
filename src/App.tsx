import { useState } from 'react';
import './App.css';

interface SearchResult {
  id: number;
  url: string;
  score: number;
}
function App() {
  const [searchText, setSearchText] = useState('');
  const [results, setResults] = useState<Array<SearchResult>>([]); // State to store search results

  async function search() {
    const response = await fetch(`/api/search?query=${encodeURIComponent(searchText)}`);
    const data = await response.json();
    setResults(data); // Update results state with fetched data
  }

  return (
    <div className="App">
      <header className="App-header">
        <input
          type="text"
          placeholder="Co chcete vyhledat?"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />
        <button onClick={search}>Search</button>
        {results.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>URL</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {results.map((item, index) => (
                <tr key={index}>
                  <td>{item.id}</td>
                  <td><a href={item.url} target="_blank" rel="noopener noreferrer">{item.url}</a></td>
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
