import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ 
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "InnoFolio - AI Career Coach",
  description: "Your AI-powered career coach for resume guidance, interview prep, job search tips, and career development.",
  keywords: ["career coach", "resume help", "interview preparation", "job search", "AI assistant"],
  authors: [{ name: "InnoFolio" }],
  openGraph: {
    title: "InnoFolio - AI Career Coach",
    description: "Get personalized career guidance powered by AI",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
