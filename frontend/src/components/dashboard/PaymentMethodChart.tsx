import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

interface PaymentMethodChartProps {
  data: Record<string, number>;
}

const PAYMENT_METHOD_LABELS: Record<string, string> = {
  tarjeta: 'Tarjeta',
  efectivo: 'Efectivo',
  transferencia: 'Transferencia',
  debito: 'Débito',
};

export const PaymentMethodChart = ({ data }: PaymentMethodChartProps) => {
  const chartData = Object.entries(data).map(([method, amount]) => ({
    method: PAYMENT_METHOD_LABELS[method] || method,
    amount,
  }));

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Gastos por Método de Pago</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="method" />
          <YAxis />
          <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
          <Legend />
          <Bar dataKey="amount" fill="#10b981" name="Monto" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
