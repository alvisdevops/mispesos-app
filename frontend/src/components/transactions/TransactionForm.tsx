import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import type { Transaction, TransactionCreate, TransactionUpdate, PaymentMethod } from '@/types';

interface TransactionFormProps {
  transaction?: Transaction;
  categories: Array<{ id: number; name: string }>;
  onSubmit: (data: TransactionCreate | TransactionUpdate) => void;
  onCancel: () => void;
}

export const TransactionForm = ({
  transaction,
  categories,
  onSubmit,
  onCancel,
}: TransactionFormProps) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    amount: transaction?.amount || 0,
    description: transaction?.description || '',
    payment_method: transaction?.payment_method || 'tarjeta' as PaymentMethod,
    transaction_date: transaction?.transaction_date
      ? new Date(transaction.transaction_date).toISOString().slice(0, 16)
      : new Date().toISOString().slice(0, 16),
    location: transaction?.location || '',
    category_id: transaction?.category_id || undefined,
  });

  const handleChange = (field: string, value: any) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (transaction) {
      // Update existing transaction
      onSubmit(formData as TransactionUpdate);
    } else {
      // Create new transaction
      onSubmit({
        ...formData,
        telegram_user_id: user!.id,
      } as TransactionCreate);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        {transaction ? 'Editar Transacción' : 'Nueva Transacción'}
      </h3>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Monto *
          </label>
          <input
            type="number"
            step="0.01"
            required
            value={formData.amount}
            onChange={(e) => handleChange('amount', parseFloat(e.target.value))}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="50000"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Descripción *
          </label>
          <input
            type="text"
            required
            value={formData.description}
            onChange={(e) => handleChange('description', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Almuerzo en restaurante"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Categoría
          </label>
          <select
            value={formData.category_id || ''}
            onChange={(e) => handleChange('category_id', e.target.value ? parseInt(e.target.value) : undefined)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">Seleccionar categoría</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Método de Pago *
          </label>
          <select
            required
            value={formData.payment_method}
            onChange={(e) => handleChange('payment_method', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="tarjeta">Tarjeta</option>
            <option value="efectivo">Efectivo</option>
            <option value="transferencia">Transferencia</option>
            <option value="debito">Débito</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Fecha y Hora *
          </label>
          <input
            type="datetime-local"
            required
            value={formData.transaction_date}
            onChange={(e) => handleChange('transaction_date', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Ubicación
          </label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => handleChange('location', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Centro Comercial"
          />
        </div>
      </div>

      <div className="flex space-x-4 mt-6">
        <button
          type="submit"
          className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          {transaction ? 'Actualizar' : 'Crear'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
        >
          Cancelar
        </button>
      </div>
    </form>
  );
};
