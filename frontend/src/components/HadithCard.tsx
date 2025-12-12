import Link from 'next/link';
import type { HadithResult, HadithListItem } from '@/lib/types';

type HadithData = HadithResult | HadithListItem;

interface HadithCardProps {
  hadith: HadithData;
  showBook?: boolean;
}

// Grade styling
const gradeStyles: Record<string, { bg: string; text: string; dot: string }> = {
  sahih: { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  hasan: { bg: 'bg-sky-50', text: 'text-sky-700', dot: 'bg-sky-500' },
  "da'if": { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
  maudu: { bg: 'bg-red-50', text: 'text-red-700', dot: 'bg-red-500' },
};

function getGradeStyle(grade: string | null) {
  if (!grade) return { bg: 'bg-stone-100', text: 'text-stone-600', dot: 'bg-stone-400' };
  const lower = grade.toLowerCase();
  for (const [key, style] of Object.entries(gradeStyles)) {
    if (lower.includes(key)) return style;
  }
  return { bg: 'bg-stone-100', text: 'text-stone-600', dot: 'bg-stone-400' };
}

// Truncate helper
function truncate(text: string | null, maxLength: number): string {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength).trim() + '...';
}

export default function HadithCard({ hadith, showBook = true }: HadithCardProps) {
  const displayText = hadith.en_text || hadith.ar_text;
  const isArabic = !hadith.en_text;
  const bookTitle = 'book_title' in hadith ? hadith.book_title : null;
  const gradeStyle = getGradeStyle(hadith.grade_text);

  return (
    <Link href={`/hadith/${hadith.hadith_id}`} className="block group">
      <article className="bg-white rounded-xl border border-stone-200 p-5 hover:border-emerald-300 hover:shadow-lg hover:shadow-emerald-100/50 transition-all duration-200">
        {/* Header */}
        <div className="flex items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-3 min-w-0">
            {showBook && bookTitle && (
              <span className="text-sm font-medium text-emerald-600 truncate">
                {bookTitle}
              </span>
            )}
            <span className="text-sm text-stone-400 shrink-0">
              Hadith #{hadith.hadith_number}
            </span>
          </div>

          {hadith.grade_text && (
            <span className={`inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full ${gradeStyle.bg} ${gradeStyle.text}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${gradeStyle.dot}`}></span>
              {hadith.grade_text}
            </span>
          )}
        </div>

        {/* Text */}
        <p
          className={`text-stone-700 leading-relaxed ${isArabic ? 'text-right font-arabic text-xl leading-loose' : 'text-base'}`}
          dir={isArabic ? 'rtl' : 'ltr'}
        >
          {truncate(displayText, 280)}
        </p>

        {/* Narrator */}
        {hadith.en_narrator && (
          <p className="mt-4 pt-4 border-t border-stone-100 text-sm text-stone-500">
            <span className="text-stone-400">Narrated by:</span>{' '}
            {truncate(hadith.en_narrator, 100)}
          </p>
        )}

        {/* Read more indicator */}
        <div className="mt-4 flex items-center gap-1 text-sm text-emerald-600 opacity-0 group-hover:opacity-100 transition-opacity">
          <span>Read full hadith</span>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </article>
    </Link>
  );
}
