import Link from 'next/link';
import SearchBar from './SearchBar';

interface HeaderProps {
  showSearch?: boolean;
  searchQuery?: string;
}

export default function Header({
  showSearch = true,
  searchQuery = '',
}: HeaderProps) {
  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-stone-200 sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-3">
        <div className="flex items-center gap-4 sm:gap-6">
          {/* Logo */}
          <Link
            href="/"
            className="flex items-center gap-2 shrink-0"
          >
            <div className="w-8 h-8 bg-emerald-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <span className="text-lg font-semibold text-stone-800 hidden sm:block">
              Hadith Search
            </span>
          </Link>

          {/* Search bar */}
          {showSearch && (
            <div className="flex-1 max-w-xl">
              <SearchBar initialQuery={searchQuery} size="normal" />
            </div>
          )}

          {/* Navigation */}
          <nav className="flex items-center gap-1">
            <Link
              href="/books"
              className="px-3 py-2 text-sm font-medium text-stone-600 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
            >
              Browse
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}
