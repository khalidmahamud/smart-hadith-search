'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import Header from '@/components/Header';
import HadithCard from '@/components/HadithCard';
import { api } from '@/lib/api';
import type { SearchResponse } from '@/lib/types';

function SearchContent() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';

  const [results, setResults] = useState<SearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query) return;

    const doSearch = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api.search(query);
        setResults(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Search failed');
      } finally {
        setIsLoading(false);
      }
    };

    doSearch();
  }, [query]);

  return (
    <div className="min-h-screen bg-stone-50">
      <Header showSearch searchQuery={query} />

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        {/* Loading */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin mb-4"></div>
            <p className="text-stone-500">Searching...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
            <p className="font-medium">Search failed</p>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}

        {/* Results */}
        {results && !isLoading && (
          <>
            {/* Result Info */}
            <div className="mb-6">
              <h1 className="text-2xl font-semibold text-stone-900 mb-1">
                {results.count === 0 ? 'No results' : `${results.count} results`}
              </h1>
              <p className="text-stone-500">
                for "<span className="text-stone-700">{results.query}</span>"
              </p>

              {/* Query Expansion */}
              {results.expansion.expanded.length > results.expansion.original.length && (
                <div className="mt-3 flex items-start gap-2 text-sm">
                  <span className="text-stone-400 shrink-0">Also searched:</span>
                  <span className="text-stone-600">
                    {results.expansion.expanded
                      .filter((t) => !results.expansion.original.includes(t))
                      .slice(0, 5)
                      .join(', ')}
                  </span>
                </div>
              )}
            </div>

            {/* Results List */}
            {results.count === 0 ? (
              <div className="text-center py-16">
                <div className="w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h2 className="text-lg font-medium text-stone-700 mb-2">No hadiths found</h2>
                <p className="text-stone-500">Try different keywords or check your spelling</p>
              </div>
            ) : (
              <div className="space-y-4">
                {results.results.map((hadith) => (
                  <HadithCard key={hadith.hadith_id} hadith={hadith} />
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-stone-50">
        <Header showSearch />
        <div className="flex justify-center py-20">
          <div className="w-10 h-10 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin"></div>
        </div>
      </div>
    }>
      <SearchContent />
    </Suspense>
  );
}
