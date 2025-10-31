// Payment methods
export type PaymentMethod = 'tarjeta' | 'efectivo' | 'transferencia' | 'debito';

// Transaction interfaces
export interface Transaction {
  id: number;
  amount: number;
  description: string;
  payment_method: PaymentMethod;
  transaction_date: string;
  location?: string;
  category_id?: number;
  category_name?: string;
  category_color?: string;
  telegram_message_id?: number;
  telegram_user_id: number;
  ai_confidence?: number;
  ai_model_used?: string;
  original_text?: string;
  is_validated: boolean;
  is_correction: boolean;
  corrected_transaction_id?: number;
  created_at: string;
  updated_at?: string;
}

export interface TransactionCreate {
  amount: number;
  description: string;
  payment_method: PaymentMethod;
  transaction_date: string;
  location?: string;
  category_id?: number;
  telegram_user_id: number;
  original_text?: string;
  ai_confidence?: number;
  ai_model_used?: string;
}

export interface TransactionUpdate {
  amount?: number;
  description?: string;
  payment_method?: PaymentMethod;
  transaction_date?: string;
  location?: string;
  category_id?: number;
  is_validated?: boolean;
}

export interface TransactionFilter {
  start_date?: string;
  end_date?: string;
  category_id?: number;
  payment_method?: PaymentMethod;
  min_amount?: number;
  max_amount?: number;
  search_text?: string;
  telegram_user_id?: number;
  is_validated?: boolean;
}

export interface TransactionSummary {
  total_amount: number;
  transaction_count: number;
  period_start: string;
  period_end: string;
  by_category: Record<string, number>;
  by_payment_method: Record<string, number>;
  daily_totals: Record<string, number>;
}

// Category interfaces
export interface Category {
  id: number;
  name: string;
  description?: string;
  color?: string;
  icon?: string;
  is_active: boolean;
  is_system: boolean;
  priority: number;
  ai_usage_count: number;
  accuracy_score: number;
  created_at: string;
  updated_at?: string;
}

// User interfaces (Telegram)
export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  photo_url?: string;
  auth_date: number;
  hash: string;
}

// Auth context
export interface AuthContextType {
  user: TelegramUser | null;
  isAuthenticated: boolean;
  login: (user: TelegramUser) => void;
  logout: () => void;
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
