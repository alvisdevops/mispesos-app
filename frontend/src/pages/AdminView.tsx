import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { transactionsService } from '@/services/transactions';
import { TransactionList } from '@/components/transactions/TransactionList';
import { TransactionFilters } from '@/components/transactions/TransactionFilters';
import { categoriesService } from '@/services/categories';
import type { TransactionFilter } from '@/types';

export const AdminView = () => {
  const [filters, setFilters] = useState<TransactionFilter>({});
  const [selectedUserId, setSelectedUserId] = useState<number | undefined>();

  const { data: allTransactions = [], isLoading } = useQuery({
    queryKey: ['transactions', 'admin', filters, selectedUserId],
    queryFn: () =>
      transactionsService.getTransactions({
        ...filters,
        telegram_user_id: selectedUserId,
      }),
  });

  const { data: categories = [] } = useQuery({
    queryKey: ['categories'],
    queryFn: () => categoriesService.getActiveCategories(),
  });

  // Get unique users from transactions
  const users = Array.from(
    new Set(allTransactions.map((t) => t.telegram_user_id))
  ).map((id) => ({
    id,
    count: allTransactions.filter((t) => t.telegram_user_id === id).length,
  }));

  // Calculate stats per user
  const userStats = users.map((user) => {
    const userTransactions = allTransactions.filter(
      (t) => t.telegram_user_id === user.id
    );
    const total = userTransactions.reduce((sum, t) => sum + t.amount, 0);
    return {
      ...user,
      total,
      validated: userTransactions.filter((t) => t.is_validated).length,
    };
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Cargando datos...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Vista de Administrador</h2>
        <p className="text-gray-600 mt-1">
          Vista completa de transacciones de todos los usuarios
        </p>
      </div>

      {/* User stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {userStats.map((user) => (
          <div
            key={user.id}
            onClick={() =>
              setSelectedUserId(selectedUserId === user.id ? undefined : user.id)
            }
            className={`bg-white rounded-lg shadow p-4 cursor-pointer transition-all ${
              selectedUserId === user.id
                ? 'ring-2 ring-primary-500'
                : 'hover:shadow-md'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">
                Usuario #{user.id}
              </span>
              {selectedUserId === user.id && (
                <span className="text-xs bg-primary-100 text-primary-600 px-2 py-1 rounded">
                  Seleccionado
                </span>
              )}
            </div>
            <p className="text-2xl font-bold text-gray-900">
              ${user.total.toLocaleString()}
            </p>
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              <span>{user.count} transacciones</span>
              <span>{user.validated} validadas</span>
            </div>
          </div>
        ))}
      </div>

      {/* Summary stats */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Estadísticas Generales
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-600">Total Usuarios</p>
            <p className="text-2xl font-bold text-gray-900">{users.length}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Transacciones</p>
            <p className="text-2xl font-bold text-gray-900">
              {allTransactions.length}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Gastos</p>
            <p className="text-2xl font-bold text-gray-900">
              ${allTransactions.reduce((sum, t) => sum + t.amount, 0).toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Promedio por Usuario</p>
            <p className="text-2xl font-bold text-gray-900">
              $
              {users.length > 0
                ? Math.round(
                    allTransactions.reduce((sum, t) => sum + t.amount, 0) /
                      users.length
                  ).toLocaleString()
                : 0}
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <TransactionFilters onFilter={setFilters} categories={categories} />

      {/* Transactions list */}
      <TransactionList
        transactions={allTransactions}
        onEdit={() => {}}
        onDelete={() => {}}
        onValidate={() => {}}
      />
    </div>
  );
};
