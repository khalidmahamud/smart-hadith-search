import type { Metadata } from 'next';
import { Inter, Noto_Naskh_Arabic } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

const notoNaskhArabic = Noto_Naskh_Arabic({
  subsets: ['arabic'],
  display: 'swap',
  variable: '--font-arabic',
  weight: ['400', '500', '600', '700'],
});

export const metadata: Metadata = {
  title: 'Smart Hadith Search',
  description: 'Search 26,742 hadiths in Arabic, English, Bengali, and Urdu with semantic search',
  keywords: ['hadith', 'search', 'islamic', 'arabic', 'quran', 'sunnah'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${notoNaskhArabic.variable}`}>
      <body className="bg-stone-50 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
