'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';

interface SearchBarProps {
  initialQuery?: string;
  size?: 'large' | 'normal';
}

export default function SearchBar({
  initialQuery = '',
  size = 'normal',
}: SearchBarProps) {
  const [query, setQuery] = useState(initialQuery);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setIsLoading(true);
      router.push(`/search?q=${encodeURIComponent(query.trim())}`);
    }
  };

  const isLarge = size === 'large';

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="relative group">
        {/* Search Icon */}
        <div className={`absolute left-0 top-1/2 -translate-y-1/2 text-stone-400 group-focus-within:text-emerald-500 transition-colors ${isLarge ? 'left-4' : 'left-3'}`}>
          <svg className={isLarge ? 'w-6 h-6' : 'w-5 h-5'} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search hadiths..."
          className={`
            w-full bg-white border border-stone-200 rounded-xl
            placeholder:text-stone-400 text-stone-800
            focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20
            outline-none transition-all duration-200
            ${isLarge
              ? 'pl-12 pr-14 py-4 text-lg shadow-sm'
              : 'pl-10 pr-12 py-2.5 text-base'
            }
          `}
          dir="auto"
        />

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className={`
            absolute right-2 top-1/2 -translate-y-1/2
            bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg
            disabled:bg-stone-200 disabled:text-stone-400 disabled:cursor-not-allowed
            transition-all duration-200
            ${isLarge ? 'p-2.5' : 'p-2'}
          `}
        >
          {isLoading ? (
            <svg className={`${isLarge ? 'w-5 h-5' : 'w-4 h-4'} animate-spin`} fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          ) : (
            <svg className={isLarge ? 'w-5 h-5' : 'w-4 h-4'} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          )}
        </button>
      </div>
    </form>
  );
}
