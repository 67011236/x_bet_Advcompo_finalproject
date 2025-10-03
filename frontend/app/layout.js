import '../styles/globals.css';
import '../styles/header.css';
import '../styles/login.css';
import '../styles/register.css';
import '../styles/balance.css';

export const metadata = {
  title: '1xBET',
  description: 'Login/Register System',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
