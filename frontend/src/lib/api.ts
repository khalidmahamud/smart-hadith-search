import type {
	SearchResponse,
	HadithDetail,
	Book,
	Chapter,
	PaginatedHadiths,
} from './types';

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// Generic fetch wrapper with error handling
async function fetchAPI<T>(
	endpoint: string,
	options?: RequestInit
): Promise<T> {
	const url = `${API_URL}${endpoint}`;
	const res = await fetch(url, {
		...options,
		headers: {
			'Content-Type': 'application/json',
			...options?.headers,
		},
	});

	if (!res.ok) {
		throw new Error(`API error: ${res.status} ${res.statusText}`);
	}

	return res.json();
}

export const api = {
	// Search hadiths
	search: (
		query: string,
		options?: { lang?: string; book_id?: number; limit?: number }
	): Promise<SearchResponse> => {
		return fetchAPI('/search', {
			method: 'POST',
			body: JSON.stringify({ query, ...options }),
		});
	},

	// Get single hadith
	getHadith: (id: number): Promise<HadithDetail> => {
		return fetchAPI(`/hadiths/${id}`);
	},

	// Get all books
	getBooks: (): Promise<{ books: Book[] }> => {
		return fetchAPI('/books');
	},

	// Get single book
	getBook: (id: number): Promise<Book> => {
		return fetchAPI(`/books/${id}`);
	},

	// Get chapters for a book
	getChapters: (
		bookId: number
	): Promise<{ book_id: number; chapters: Chapter[] }> => {
		return fetchAPI(`/books/${bookId}/chapters`);
	},

	// Get hadiths for a book (paginated)
	getBookHadiths: (
		bookId: number,
		options?: { chapter_id?: number; page?: number; per_page?: number }
	): Promise<PaginatedHadiths> => {
		const params = new URLSearchParams();
		if (options?.chapter_id)
			params.set('chapter_id', String(options.chapter_id));
		if (options?.page) params.set('page', String(options.page));
		if (options?.per_page) params.set('per_page', String(options.per_page));

		const query = params.toString();
		return fetchAPI(`/books/${bookId}/hadiths${query ? `?${query}` : ''}`);
	},
};
