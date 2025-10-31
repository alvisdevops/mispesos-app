import { useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import type { TelegramUser } from '@/types';

interface TelegramLoginProps {
  botName: string;
  buttonSize?: 'large' | 'medium' | 'small';
  cornerRadius?: number;
  requestAccess?: boolean;
  usePic?: boolean;
  lang?: string;
}

declare global {
  interface Window {
    TelegramLoginWidget?: {
      dataOnauth?: (user: TelegramUser) => void;
    };
  }
}

export const TelegramLogin = ({
  botName,
  buttonSize = 'large',
  cornerRadius = 10,
  requestAccess = true,
  usePic = true,
  lang = 'es',
}: TelegramLoginProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    // Define the callback function
    window.TelegramLoginWidget = {
      dataOnauth: (user: TelegramUser) => {
        console.log('Telegram auth successful:', user);
        login(user);
        navigate('/dashboard');
      },
    };

    // Create script element
    const script = document.createElement('script');
    script.src = 'https://telegram.org/js/telegram-widget.js?22';
    script.setAttribute('data-telegram-login', botName);
    script.setAttribute('data-size', buttonSize);
    script.setAttribute('data-radius', cornerRadius.toString());
    script.setAttribute('data-request-access', requestAccess ? 'write' : '');
    script.setAttribute('data-userpic', usePic.toString());
    script.setAttribute('data-lang', lang);
    script.setAttribute('data-onauth', 'TelegramLoginWidget.dataOnauth(user)');
    script.async = true;

    // Append script to container
    if (containerRef.current) {
      containerRef.current.appendChild(script);
    }

    // Cleanup
    return () => {
      if (containerRef.current && script.parentNode) {
        containerRef.current.removeChild(script);
      }
      delete window.TelegramLoginWidget;
    };
  }, [botName, buttonSize, cornerRadius, requestAccess, usePic, lang, login, navigate]);

  return <div ref={containerRef} className="flex justify-center" />;
};
