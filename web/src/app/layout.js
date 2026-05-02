import './globals.css';

export const metadata = {
  title: 'NaviRaksha — Emergency Intelligence',
  description: 'AI-Powered Emergency Response for Navi Mumbai',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
