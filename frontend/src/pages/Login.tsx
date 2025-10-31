import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { TelegramLogin } from '@/components/auth/TelegramLogin';

export const Login = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  const botName = import.meta.env.VITE_TELEGRAM_BOT_NAME || 'MisPesosBot';

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">MisPesos</h1>
          <p className="text-gray-600">Gestión inteligente de gastos personales</p>
        </div>

        <div className="mb-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-blue-800">
              Inicia sesión con tu cuenta de Telegram para acceder a tu dashboard financiero.
            </p>
          </div>
        </div>

        <div className="flex justify-center">
          <TelegramLogin botName={botName} />
        </div>

        <div className="mt-8 text-center text-sm text-gray-500">
          <p>¿No tienes el bot de Telegram?</p>
          <a
            href={`https://t.me/${botName}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-600 hover:text-primary-700 font-medium"
          >
            Haz clic aquí para iniciarlo
          </a>
        </div>
      </div>
    </div>
  );
};
