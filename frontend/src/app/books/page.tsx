import Header from '@/components/Header';
import Link from 'next/link';
import type { Book } from '@/lib/types';

async function getBooks(): Promise<Book[]> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/books`, {
      cache: 'no-store',
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.books;
  } catch {
    return [];
  }
}

export default async function BooksPage() {
  const books = await getBooks();

  return (
    <div className="min-h-screen bg-stone-50">
      <Header showSearch />

      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-stone-900 mb-2">
            Hadith Collections
          </h1>
          <p className="text-stone-500">
            Browse through authentic hadith books
          </p>
        </div>

        {/* Books Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {books.map((book) => (
            <Link key={book.book_id} href={`/books/${book.book_id}`} className="group">
              <article className="bg-white rounded-2xl border border-stone-200 p-6 h-full hover:border-emerald-300 hover:shadow-lg hover:shadow-emerald-100/50 transition-all duration-200">
                <div className="flex items-start justify-between gap-3 mb-4">
                  <div className="w-10 h-10 bg-emerald-100 rounded-xl flex items-center justify-center shrink-0">
                    <svg className="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <span className="text-xs font-medium text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full">
                    {book.hadith_count.toLocaleString()} hadiths
                  </span>
                </div>

                <h2 className="text-lg font-semibold text-stone-900 mb-2 group-hover:text-emerald-700 transition-colors">
                  {book.en_title}
                </h2>

                {book.ar_title && (
                  <p className="text-stone-500 text-right font-arabic text-lg" dir="rtl">
                    {book.ar_title}
                  </p>
                )}

                <div className="mt-4 pt-4 border-t border-stone-100 flex items-center gap-1 text-sm text-emerald-600 opacity-0 group-hover:opacity-100 transition-opacity">
                  <span>View collection</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </article>
            </Link>
          ))}
        </div>

        {/* Empty State */}
        {books.length === 0 && (
          <div className="text-center py-16">
            <div className="w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-stone-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h2 className="text-lg font-medium text-stone-700 mb-2">No books found</h2>
            <p className="text-stone-500">Make sure the backend server is running</p>
          </div>
        )}
      </main>
    </div>
  );
}
