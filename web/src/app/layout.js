import './globals.css';

export const metadata = {
  title: 'NaviRaksha — Emergency Intelligence',
  description: 'AI-Powered Emergency Response for Navi Mumbai',
  icons: {
    icon: '/favicon.png',
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
