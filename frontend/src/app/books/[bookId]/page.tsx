'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Header from '@/components/Header';
import HadithCard from '@/components/HadithCard';
import Pagination from '@/components/Pagination';
import { api } from '@/lib/api';
import type { Book, PaginatedHadiths } from '@/lib/types';

export default function BookDetailPage() {
	const params = useParams();
	const bookId = Number(params.bookId);

	const [book, setBook] = useState<Book | null>(null);
	const [hadiths, setHadiths] = useState<PaginatedHadiths | null>(null);
	const [page, setPage] = useState(1);
	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		const fetchBook = async () => {
			try {
				const bookData = await api.getBook(bookId);
				setBook(bookData);
			} catch (err) {
				console.error('Failed to fetch book:', err);
			}
		};
		fetchBook();
	}, [bookId]);

	useEffect(() => {
		const fetchHadiths = async () => {
			setIsLoading(true);
			try {
				const data = await api.getBookHadiths(bookId, { page, per_page: 20 });
				setHadiths(data);
			} catch (err) {
				console.error('Failed to fetch hadiths:', err);
			} finally {
				setIsLoading(false);
			}
		};
		fetchHadiths();
	}, [bookId, page]);

	const handlePageChange = (newPage: number) => {
		setPage(newPage);
		window.scrollTo({ top: 0, behavior: 'smooth' });
	};

	return (
		<div className='min-h-screen bg-stone-50'>
			<Header showSearch />

			<main className='max-w-3xl mx-auto px-4 sm:px-6 py-8'>
				{/* Breadcrumb */}
				<nav className='flex items-center gap-2 text-sm text-stone-500 mb-8'>
					<Link
						href='/'
						className='hover:text-emerald-600 transition-colors'
					>
						Home
					</Link>
					<svg
						className='w-4 h-4 text-stone-300'
						fill='none'
						stroke='currentColor'
						viewBox='0 0 24 24'
					>
						<path
							strokeLinecap='round'
							strokeLinejoin='round'
							strokeWidth={2}
							d='M9 5l7 7-7 7'
						/>
					</svg>
					<Link
						href='/books'
						className='hover:text-emerald-600 transition-colors'
					>
						Books
					</Link>
					{book && (
						<>
							<svg
								className='w-4 h-4 text-stone-300'
								fill='none'
								stroke='currentColor'
								viewBox='0 0 24 24'
							>
								<path
									strokeLinecap='round'
									strokeLinejoin='round'
									strokeWidth={2}
									d='M9 5l7 7-7 7'
								/>
							</svg>
							<span className='text-stone-700 font-medium truncate'>
								{book.en_title}
							</span>
						</>
					)}
				</nav>

				{/* Book Header */}
				{book && (
					<div className='bg-white rounded-2xl border border-stone-200 p-6 mb-8'>
						<div className='flex items-start gap-4'>
							<div className='w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center shrink-0'>
								<svg
									className='w-6 h-6 text-emerald-600'
									fill='none'
									stroke='currentColor'
									viewBox='0 0 24 24'
								>
									<path
										strokeLinecap='round'
										strokeLinejoin='round'
										strokeWidth={2}
										d='M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253'
									/>
								</svg>
							</div>
							<div className='flex-1 min-w-0'>
								<h1 className='text-2xl font-bold text-stone-900 mb-1'>
									{book.en_title}
								</h1>
								{book.ar_title && (
									<p
										className='text-lg text-stone-500 font-arabic'
										dir='rtl'
									>
										{book.ar_title}
									</p>
								)}
								<p className='mt-3 text-sm text-emerald-600 font-medium'>
									{book.hadith_count.toLocaleString()} hadiths in this
									collection
								</p>
							</div>
						</div>
					</div>
				)}

				{/* Loading */}
				{isLoading && (
					<div className='flex flex-col items-center justify-center py-20'>
						<div className='w-10 h-10 border-4 border-emerald-200 border-t-emerald-600 rounded-full animate-spin mb-4'></div>
						<p className='text-stone-500'>Loading hadiths...</p>
					</div>
				)}

				{/* Hadiths List */}
				{hadiths && !isLoading && (
					<>
						{/* Page Info */}
						<div className='flex items-center justify-between mb-4'>
							<p className='text-sm text-stone-500'>
								Showing {(page - 1) * 20 + 1}-
								{Math.min(page * 20, hadiths.total)} of{' '}
								{hadiths.total.toLocaleString()}
							</p>
						</div>

						<div className='space-y-4'>
							{hadiths.results.map((hadith) => (
								<HadithCard
									key={hadith.hadith_id}
									hadith={hadith}
									showBook={false}
								/>
							))}
						</div>

						<Pagination
							currentPage={hadiths.page}
							totalPages={hadiths.pages}
							onPageChange={handlePageChange}
						/>
					</>
				)}
			</main>
		</div>
	);
}
