import "./globals.css";

export const metadata = {
  title: "Trace — Evidence workspace",
  description: "Evidence-first people investigations.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
