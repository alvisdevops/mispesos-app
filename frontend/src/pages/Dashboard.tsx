import { useQuery } from '@tanstack/react-query';
import { transactionsService } from '@/services/transactions';
import { StatsCard } from '@/components/dashboard/StatsCard';
import { CategoryChart } from '@/components/dashboard/CategoryChart';
import { DailyChart } from '@/components/dashboard/DailyChart';
import { PaymentMethodChart } from '@/components/dashboard/PaymentMethodChart';

export const Dashboard = () => {
  const { data: weeklySummary, isLoading: loadingWeekly } = useQuery({
    queryKey: ['summary', 'weekly'],
    queryFn: () => transactionsService.getSummary('weekly'),
  });

  const { data: monthlySummary, isLoading: loadingMonthly } = useQuery({
    queryKey: ['summary', 'monthly'],
    queryFn: () => transactionsService.getSummary('monthly'),
  });

  if (loadingWeekly || loadingMonthly) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Cargando dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-600 mt-1">Vista general de tus gastos</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Gastos Esta Semana"
          value={`$${weeklySummary?.total_amount.toLocaleString() || 0}`}
          icon="📊"
          color="blue"
          subtitle={`${weeklySummary?.transaction_count || 0} transacciones`}
        />
        <StatsCard
          title="Gastos Este Mes"
          value={`$${monthlySummary?.total_amount.toLocaleString() || 0}`}
          icon="💰"
          color="green"
          subtitle={`${monthlySummary?.transaction_count || 0} transacciones`}
        />
        <StatsCard
          title="Promedio Diario (Mes)"
          value={`$${Math.round((monthlySummary?.total_amount || 0) / 30).toLocaleString()}`}
          icon="📈"
          color="purple"
        />
        <StatsCard
          title="Transacciones Hoy"
          value={Object.keys(weeklySummary?.daily_totals || {}).length}
          icon="🔄"
          color="yellow"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {weeklySummary?.by_category && (
          <CategoryChart data={weeklySummary.by_category} />
        )}
        {weeklySummary?.by_payment_method && (
          <PaymentMethodChart data={weeklySummary.by_payment_method} />
        )}
      </div>

      {/* Daily Chart */}
      {monthlySummary?.daily_totals && (
        <DailyChart data={monthlySummary.daily_totals} />
      )}
    </div>
  );
};
