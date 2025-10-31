import api from './api';
import type {
  Transaction,
  TransactionCreate,
  TransactionUpdate,
  TransactionFilter,
  TransactionSummary,
} from '@/types';

export const transactionsService = {
  // Get all transactions with optional filters
  getTransactions: async (filters?: TransactionFilter) => {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
    }
    const response = await api.get<Transaction[]>(`/transactions?${params.toString()}`);
    return response.data;
  },

  // Get single transaction
  getTransaction: async (id: number) => {
    const response = await api.get<Transaction>(`/transactions/${id}`);
    return response.data;
  },

  // Create transaction
  createTransaction: async (data: TransactionCreate) => {
    const response = await api.post<Transaction>('/transactions', data);
    return response.data;
  },

  // Update transaction
  updateTransaction: async (id: number, data: TransactionUpdate) => {
    const response = await api.put<Transaction>(`/transactions/${id}`, data);
    return response.data;
  },

  // Delete transaction
  deleteTransaction: async (id: number) => {
    await api.delete(`/transactions/${id}`);
  },

  // Validate transaction
  validateTransaction: async (id: number) => {
    const response = await api.post<Transaction>(`/transactions/${id}/validate`);
    return response.data;
  },

  // Get summary
  getSummary: async (period: 'daily' | 'weekly' | 'monthly') => {
    const response = await api.get<TransactionSummary>(`/transactions/summary/${period}`);
    return response.data;
  },

  // Get quick balance
  getBalance: async () => {
    const response = await api.get<{ total: number }>('/transactions/balance/quick');
    return response.data;
  },
};

export default transactionsService;
