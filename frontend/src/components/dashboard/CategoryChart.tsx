import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface CategoryChartProps {
  data: Record<string, number>;
}

const COLORS = [
  '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8',
  '#82CA9D', '#FFC658', '#FF6B9D', '#C2B280', '#A8D5BA'
];

export const CategoryChart = ({ data }: CategoryChartProps) => {
  const chartData = Object.entries(data).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Gastos por Categoría</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value: number) => `$${value.toLocaleString()}`} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
