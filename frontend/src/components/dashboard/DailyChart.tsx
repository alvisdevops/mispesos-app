import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { format, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';

interface DailyChartProps {
  data: Record<string, number>;
}

export const DailyChart = ({ data }: DailyChartProps) => {
  const chartData = Object.entries(data)
    .map(([date, amount]) => ({
      date: format(parseISO(date), 'dd/MM', { locale: es }),
      amount,
    }))
    .slice(-14); // Last 14 days

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Gastos Diarios (últimos 14 días)</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
          <Legend />
          <Bar dataKey="amount" fill="#0ea5e9" name="Monto" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
