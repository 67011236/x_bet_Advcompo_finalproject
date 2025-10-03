'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect ไปหน้า login ทันที
    router.push('/login');
  }, [router]);

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh',
      backgroundColor: '#0d1421',
      color: 'white'
    }}>
      <div>
        <h1>1xBET</h1>
        <p>Redirecting to login...</p>
      </div>
    </div>
  );
}
