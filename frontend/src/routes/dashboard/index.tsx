import { useAuthStore } from '@/hooks/useAuth';
import AnalystDashboard from '@/components/dashboard/AnalystDashboard';
import DecisionMakerDashboard from '@/components/dashboard/DecisionMakerDashboard';

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user);

  if (!user) return null;

  return user.role === 'analyst' ? (
    <AnalystDashboard />
  ) : (
    <DecisionMakerDashboard />
  );
}