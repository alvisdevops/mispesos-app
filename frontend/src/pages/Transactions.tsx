import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { transactionsService } from '@/services/transactions';
import { categoriesService } from '@/services/categories';
import { TransactionList } from '@/components/transactions/TransactionList';
import { TransactionFilters } from '@/components/transactions/TransactionFilters';
import { TransactionForm } from '@/components/transactions/TransactionForm';
import type { Transaction, TransactionFilter, TransactionUpdate } from '@/types';

export const Transactions = () => {
  const [filters, setFilters] = useState<TransactionFilter>({});
  const [editingTransaction, setEditingTransaction] = useState<Transaction | null>(null);
  const [showEditForm, setShowEditForm] = useState(false);

  const queryClient = useQueryClient();

  const { data: transactions = [], isLoading: loadingTransactions } = useQuery({
    queryKey: ['transactions', filters],
    queryFn: () => transactionsService.getTransactions(filters),
  });

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoriesService.getActiveCategories(),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: TransactionUpdate }) =>
      transactionsService.updateTransaction(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      setShowEditForm(false);
      setEditingTransaction(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => transactionsService.deleteTransaction(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
    },
  });

  const validateMutation = useMutation({
    mutationFn: (id: number) => transactionsService.validateTransaction(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
    },
  });

  const handleEdit = (transaction: Transaction) => {
    setEditingTransaction(transaction);
    setShowEditForm(true);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('¿Estás seguro de eliminar esta transacción?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleValidate = (id: number) => {
    validateMutation.mutate(id);
  };

  const handleUpdate = (data: TransactionUpdate) => {
    if (editingTransaction) {
      updateMutation.mutate({ id: editingTransaction.id, data });
    }
  };

  if (loadingTransactions) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Cargando transacciones...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Transacciones</h2>
        <p className="text-gray-600 mt-1">Historial completo de gastos</p>
      </div>

      <TransactionFilters onFilter={setFilters} categories={categories} />

      {showEditForm && editingTransaction && (
        <TransactionForm
          transaction={editingTransaction}
          categories={categories}
          onSubmit={handleUpdate}
          onCancel={() => {
            setShowEditForm(false);
            setEditingTransaction(null);
          }}
        />
      )}

      <TransactionList
        transactions={transactions}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onValidate={handleValidate}
      />
    </div>
  );
};
