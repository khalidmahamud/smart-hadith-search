import SearchBar from '@/components/SearchBar';
import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-20">
        {/* Logo */}
        <div className="w-16 h-16 bg-emerald-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg shadow-emerald-200">
          <svg className="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>

        <h1 className="text-4xl sm:text-5xl font-bold text-stone-900 mb-4 text-center tracking-tight">
          Smart Hadith Search
        </h1>
        <p className="text-lg text-stone-500 mb-10 text-center max-w-lg leading-relaxed">
          Search through 26,742 hadiths in Arabic, English, Bengali, and Urdu with intelligent query expansion
        </p>

        {/* Search Bar */}
        <div className="w-full max-w-xl mb-10">
          <SearchBar size="large" />
        </div>

        {/* Features */}
        <div className="flex flex-wrap justify-center gap-x-8 gap-y-3 text-sm text-stone-500">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
            <span>Phonetic matching</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
            <span>Fuzzy search</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-500 rounded-full"></div>
            <span>Multi-language support</span>
          </div>
        </div>
      </div>

      {/* Browse Section */}
      <div className="text-center pb-12">
        <Link
          href="/books"
          className="inline-flex items-center gap-2 text-emerald-600 hover:text-emerald-700 font-medium transition-colors"
        >
          <span>Browse hadith collections</span>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </Link>
      </div>

      {/* Footer */}
      <footer className="border-t border-stone-200 py-6">
        <p className="text-center text-sm text-stone-400">
          Powered by FTS5 full-text search
        </p>
      </footer>
    </main>
  );
}
