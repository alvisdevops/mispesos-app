import api from './api';
import type { Category } from '@/types';

export const categoriesService = {
  // Get all categories
  getCategories: async () => {
    const response = await api.get<Category[]>('/categories');
    return response.data;
  },

  // Get active categories only
  getActiveCategories: async () => {
    const response = await api.get<Category[]>('/categories?is_active=true');
    return response.data;
  },
};

export default categoriesService;
