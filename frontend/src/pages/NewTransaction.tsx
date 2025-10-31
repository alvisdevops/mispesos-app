import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionsService } from '@/services/transactions';
import { categoriesService } from '@/services/categories';
import { TransactionForm } from '@/components/transactions/TransactionForm';
import type { TransactionCreate } from '@/types';

export const NewTransaction = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoriesService.getActiveCategories(),
  });

  const createMutation = useMutation({
    mutationFn: (data: TransactionCreate) => transactionsService.createTransaction(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      queryClient.invalidateQueries({ queryKey: ['summary'] });
      navigate('/transactions');
    },
  });

  const handleSubmit = (data: TransactionCreate) => {
    createMutation.mutate(data);
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Nueva Transacción</h2>
        <p className="text-gray-600 mt-1">Registra un nuevo gasto manualmente</p>
      </div>

      <TransactionForm
        categories={categories}
        onSubmit={handleSubmit}
        onCancel={() => navigate('/transactions')}
      />

      {createMutation.isError && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">
            Error al crear la transacción. Por favor intenta nuevamente.
          </p>
        </div>
      )}
    </div>
  );
};
