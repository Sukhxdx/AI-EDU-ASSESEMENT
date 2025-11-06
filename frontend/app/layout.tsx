import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "AI Edu Assessment",
  description: "Quality education tools: readability, glossary, quizzes",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">
        <header className="border-b bg-white">
          <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-6">
            <h1 className="font-semibold text-lg">AI Edu Assessment</h1>
            <nav className="text-sm flex gap-4">
              <a href="/" className="hover:underline">Home</a>
              <a href="/analyze" className="hover:underline">Analyze</a>
              <a href="/quizzes" className="hover:underline">Quizzes</a>
              <a href="/settings" className="hover:underline">Settings</a>
            </nav>
          </div>
        </header>
        <main className="max-w-5xl mx-auto p-4">{children}</main>
      </body>
    </html>
  );
}


