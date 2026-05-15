import { useNavigate } from '@tanstack/react-router';
import { useAuthStore } from '@/hooks/useAuth';
import LoginForm from '@/components/auth/LoginForm';

export default function LoginPage() {
  const navigate = useNavigate();
  const login = useAuthStore((state) => state.login);

  const handleLogin = async (credentials: any) => {
    await login(credentials);
    navigate({ to: '/dashboard' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 to-purple-600 flex items-center justify-center">
      <LoginForm onLogin={handleLogin} />
    </div>
  );
}