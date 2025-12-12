import { notFound } from 'next/navigation';
import Header from '@/components/Header';
import Link from 'next/link';
import type { HadithDetail } from '@/lib/types';

async function getHadith(id: string): Promise<HadithDetail | null> {
  try {
    const res = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/hadiths/${id}`,
      { cache: 'no-store' }
    );
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

// Grade styling
const gradeStyles: Record<string, { bg: string; text: string; border: string }> = {
  sahih: { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  hasan: { bg: 'bg-sky-50', text: 'text-sky-700', border: 'border-sky-200' },
  "da'if": { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
};

function getGradeStyle(grade: string | null) {
  if (!grade) return { bg: 'bg-stone-50', text: 'text-stone-600', border: 'border-stone-200' };
  const lower = grade.toLowerCase();
  for (const [key, style] of Object.entries(gradeStyles)) {
    if (lower.includes(key)) return style;
  }
  return { bg: 'bg-stone-50', text: 'text-stone-600', border: 'border-stone-200' };
}

export default async function HadithPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const hadith = await getHadith(id);

  if (!hadith) {
    notFound();
  }

  const gradeStyle = getGradeStyle(hadith.grade_text);

  return (
    <div className="min-h-screen bg-stone-50">
      <Header showSearch />

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8">
        {/* Breadcrumb */}
        <nav className="flex items-center gap-2 text-sm text-stone-500 mb-8">
          <Link href="/" className="hover:text-emerald-600 transition-colors">
            Home
          </Link>
          <svg className="w-4 h-4 text-stone-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <Link href="/books" className="hover:text-emerald-600 transition-colors">
            Books
          </Link>
          <svg className="w-4 h-4 text-stone-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          <span className="text-stone-700 font-medium truncate">{hadith.book_title}</span>
        </nav>

        {/* Header Card */}
        <div className="bg-white rounded-2xl border border-stone-200 p-6 mb-6">
          <div className="flex flex-wrap items-start justify-between gap-4 mb-4">
            <div>
              <h1 className="text-2xl font-bold text-stone-900 mb-1">
                {hadith.book_title}
              </h1>
              <p className="text-stone-500">
                Hadith #{hadith.hadith_number}
              </p>
            </div>
            {hadith.grade_text && (
              <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border ${gradeStyle.bg} ${gradeStyle.text} ${gradeStyle.border}`}>
                {hadith.grade_text}
              </span>
            )}
          </div>
          <p className="text-stone-600">{hadith.chapter_title}</p>
        </div>

        {/* Arabic Text */}
        <section className="mb-6">
          <div className="flex items-center gap-2 mb-3">
            <h2 className="text-sm font-semibold text-stone-700 uppercase tracking-wide">Arabic</h2>
            <div className="flex-1 h-px bg-stone-200"></div>
          </div>
          <div className="bg-white rounded-2xl border border-stone-200 p-6">
            <p
              className="text-2xl leading-[2.5] text-stone-800 text-right font-arabic"
              dir="rtl"
            >
              {hadith.ar_text}
            </p>
            {hadith.ar_narrator && (
              <p className="mt-6 pt-4 border-t border-stone-100 text-stone-600 text-right text-lg font-arabic" dir="rtl">
                {hadith.ar_narrator}
              </p>
            )}
          </div>
        </section>

        {/* English Text */}
        {hadith.en_text && (
          <section className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <h2 className="text-sm font-semibold text-stone-700 uppercase tracking-wide">English</h2>
              <div className="flex-1 h-px bg-stone-200"></div>
            </div>
            <div className="bg-white rounded-2xl border border-stone-200 p-6">
              <p className="text-stone-700 leading-relaxed text-lg">
                {hadith.en_text}
              </p>
              {hadith.en_narrator && (
                <p className="mt-6 pt-4 border-t border-stone-100 text-stone-500">
                  <span className="text-stone-400">Narrated by:</span> {hadith.en_narrator}
                </p>
              )}
            </div>
          </section>
        )}

        {/* Bengali Text */}
        {hadith.bn_text && (
          <section className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <h2 className="text-sm font-semibold text-stone-700 uppercase tracking-wide">Bengali</h2>
              <div className="flex-1 h-px bg-stone-200"></div>
            </div>
            <div className="bg-white rounded-2xl border border-stone-200 p-6">
              <p className="text-stone-700 leading-relaxed text-lg">
                {hadith.bn_text}
              </p>
              {hadith.bn_narrator && (
                <p className="mt-6 pt-4 border-t border-stone-100 text-stone-500">
                  <span className="text-stone-400">Narrated by:</span> {hadith.bn_narrator}
                </p>
              )}
            </div>
          </section>
        )}

        {/* Urdu Text */}
        {hadith.ur_text && (
          <section className="mb-6">
            <div className="flex items-center gap-2 mb-3">
              <h2 className="text-sm font-semibold text-stone-700 uppercase tracking-wide">Urdu</h2>
              <div className="flex-1 h-px bg-stone-200"></div>
            </div>
            <div className="bg-white rounded-2xl border border-stone-200 p-6">
              <p className="text-stone-700 leading-[2] text-right text-lg" dir="rtl">
                {hadith.ur_text}
              </p>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
