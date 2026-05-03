import { useState } from 'react';
import { Link } from 'react-router-dom';
import { AppLayout } from '../components/AppLayout';
import { searchAPI, SearchResult } from '../api/search';
import { Search, Hash, MessageSquare, Calendar } from 'lucide-react';

export function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setHasSearched(true);

    try {
      const data = await searchAPI.searchMessages(query);
      setResults(data);
    } catch (error) {
      console.error('Error searching:', error);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout>
      <div className="h-full overflow-y-auto bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Search Messages</h1>

          <form onSubmit={handleSearch} className="flex space-x-4">
            <div className="flex-1 relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search messages..."
                className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </form>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : hasSearched ? (
          results.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
              <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
              <p className="text-gray-600">
                Try searching with different keywords
              </p>
            </div>
          ) : (
            <div>
              <div className="mb-4 text-sm text-gray-600">
                Found {results.length} result{results.length !== 1 ? 's' : ''}
              </div>

              <div className="space-y-4">
                {results.map((result) => (
                  <Link
                    key={result.id}
                    to={`/channels/${result.channel}`}
                    className="block bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <div className="font-medium text-gray-900">
                          {result.sender.username}
                        </div>
                        <span className="text-gray-400">in</span>
                        <div className="flex items-center space-x-1 text-blue-600">
                          <Hash className="h-4 w-4" />
                          <span className="font-medium">{result.channel_name}</span>
                        </div>
                        <span className="text-gray-400">/</span>
                        <span className="text-gray-600">{result.workspace_name}</span>
                      </div>
                      <div className="flex items-center text-xs text-gray-500">
                        <Calendar className="h-3 w-3 mr-1" />
                        {new Date(result.created_at).toLocaleString()}
                      </div>
                    </div>

                    <p className="text-gray-700 whitespace-pre-wrap break-words">
                      {highlightQuery(result.body, query)}
                    </p>
                  </Link>
                ))}
              </div>
            </div>
          )
        ) : (
          <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
            <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Search for messages</h3>
            <p className="text-gray-600">
              Enter a keyword to search across all accessible messages
            </p>
          </div>
        )}
        </div>
      </div>
    </AppLayout>
  );
}

function highlightQuery(text: string, query: string): React.ReactNode {
  if (!query.trim()) return text;

  const parts = text.split(new RegExp(`(${query})`, 'gi'));
  return parts.map((part, index) =>
    part.toLowerCase() === query.toLowerCase() ? (
      <mark key={index} className="bg-yellow-200 font-medium">
        {part}
      </mark>
    ) : (
      <span key={index}>{part}</span>
    )
  );
}
