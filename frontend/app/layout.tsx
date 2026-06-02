import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Royalty-Free Music Generator",
  description:
    "Generate original, instrumental, royalty-free background music for live streams and videos.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
