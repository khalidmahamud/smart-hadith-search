// Types matching backend Pydantic schemas

export interface HadithResult {
  hadith_id: number;
  book_id: number;
  chapter_id: number;
  hadith_number: number;
  grade_id: number | null;
  en_text: string | null;
  ar_text: string;
  bn_text: string | null;
  ur_text: string | null;
  en_narrator: string | null;
  ar_narrator: string | null;
  bn_narrator: string | null;
  ur_narrator: string | null;
  book_title: string;
  book_title_bn: string | null;
  book_slug: string;
  grade_text: string | null;
  grade_text_bn: string | null;
  score: number;
}

export interface SearchResponse {
  query: string;
  query_lang: string;
  count: number;
  results: HadithResult[];
}

export interface HadithDetail {
  hadith_id: number;
  book_id: number;
  chapter_id: number;
  hadith_number: number;
  grade_id: number | null;
  ar_text: string;
  ar_narrator: string | null;
  en_text: string | null;
  en_narrator: string | null;
  bn_text: string | null;
  bn_narrator: string | null;
  ur_text: string | null;
  ur_narrator: string | null;
  book_title: string;
  book_slug: string;
  chapter_title: string;
  grade_text: string | null;
}

export interface Book {
  book_id: number;
  slug: string;
  en_title: string;
  ar_title: string | null;
  bn_title: string | null;
  ur_title: string | null;
  description: string | null;
  hadith_count: number;
}

export interface Chapter {
  chapter_id: number;
  order_index: number;
  en_title: string | null;
  ar_title: string | null;
  bn_title: string | null;
  ur_title: string | null;
  hadith_count: number;
}

export interface HadithListItem {
  hadith_id: number;
  book_id: number;
  chapter_id: number;
  hadith_number: number;
  grade_id: number | null;
  ar_text: string;
  ar_narrator: string | null;
  en_text: string | null;
  en_narrator: string | null;
  bn_text: string | null;
  bn_narrator: string | null;
  ur_text: string | null;
  ur_narrator: string | null;
  grade_text: string | null;
}

export interface PaginatedHadiths {
  results: HadithListItem[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}