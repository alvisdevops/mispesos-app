"""
Transaction business logic service
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionSummary,
    TransactionFilter
)


class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    async def create_transaction(self, transaction_data: TransactionCreate) -> TransactionResponse:
        """Create a new transaction"""

        # Create transaction instance
        db_transaction = Transaction(
            amount=transaction_data.amount,
            description=transaction_data.description,
            payment_method=transaction_data.payment_method,
            transaction_date=transaction_data.transaction_date,
            location=transaction_data.location,
            category_id=transaction_data.category_id,
            telegram_message_id=transaction_data.telegram_message_id,
            telegram_user_id=transaction_data.telegram_user_id,
            original_text=transaction_data.original_text,
            ai_confidence=transaction_data.ai_confidence,
            ai_model_used=transaction_data.ai_model_used
        )

        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)

        response = await self._transaction_to_response(db_transaction)

        # Trigger SSE broadcast for real-time updates
        try:
            from app.api.transactions import broadcast_transaction_update
            await broadcast_transaction_update(response.dict())
        except Exception as e:
            # Don't fail transaction creation if SSE broadcast fails
            print(f"SSE broadcast failed: {e}")

        return response

    async def get_transactions(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[TransactionFilter] = None
    ) -> List[TransactionResponse]:
        """Get transactions with optional filtering"""

        query = self.db.query(Transaction).options(joinedload(Transaction.category))

        # Apply filters
        if filters:
            if filters.start_date:
                query = query.filter(Transaction.transaction_date >= filters.start_date)
            if filters.end_date:
                query = query.filter(Transaction.transaction_date <= filters.end_date)
            if filters.category_id:
                query = query.filter(Transaction.category_id == filters.category_id)
            if filters.payment_method:
                query = query.filter(Transaction.payment_method == filters.payment_method)
            if filters.min_amount:
                query = query.filter(Transaction.amount >= filters.min_amount)
            if filters.max_amount:
                query = query.filter(Transaction.amount <= filters.max_amount)
            if filters.telegram_user_id:
                query = query.filter(Transaction.telegram_user_id == filters.telegram_user_id)
            if filters.is_validated is not None:
                query = query.filter(Transaction.is_validated == filters.is_validated)
            if filters.search_text:
                search_pattern = f"%{filters.search_text}%"
                query = query.filter(
                    or_(
                        Transaction.description.ilike(search_pattern),
                        Transaction.location.ilike(search_pattern),
                        Transaction.original_text.ilike(search_pattern)
                    )
                )

        # Order by transaction date (most recent first)
        query = query.order_by(Transaction.transaction_date.desc())

        # Apply pagination
        transactions = query.offset(skip).limit(limit).all()

        # Convert to response format
        return [await self._transaction_to_response(t) for t in transactions]

    async def get_transaction(self, transaction_id: int) -> Optional[TransactionResponse]:
        """Get a specific transaction by ID"""

        transaction = self.db.query(Transaction)\
            .options(joinedload(Transaction.category))\
            .filter(Transaction.id == transaction_id)\
            .first()

        if not transaction:
            return None

        return await self._transaction_to_response(transaction)

    async def update_transaction(
        self,
        transaction_id: int,
        update_data: TransactionUpdate
    ) -> Optional[TransactionResponse]:
        """Update an existing transaction"""

        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

        if not transaction:
            return None

        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(transaction, field, value)

        self.db.commit()
        self.db.refresh(transaction)

        return await self._transaction_to_response(transaction)

    async def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction"""

        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

        if not transaction:
            return False

        self.db.delete(transaction)
        self.db.commit()
        return True

    async def validate_transaction(self, transaction_id: int) -> Optional[TransactionResponse]:
        """Mark a transaction as validated by the user"""

        transaction = self.db.query(Transaction).filter(Transaction.id == transaction_id).first()

        if not transaction:
            return None

        transaction.is_validated = True
        self.db.commit()
        self.db.refresh(transaction)

        return await self._transaction_to_response(transaction)

    async def get_daily_summary(
        self,
        date: datetime,
        telegram_user_id: Optional[int] = None
    ) -> TransactionSummary:
        """Get summary for a specific day"""

        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)

        return await self.get_period_summary(start_date, end_date, telegram_user_id)

    async def get_period_summary(
        self,
        start_date: datetime,
        end_date: datetime,
        telegram_user_id: Optional[int] = None
    ) -> TransactionSummary:
        """Get summary for a date range"""

        # Base query
        query = self.db.query(Transaction).filter(
            and_(
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date < end_date
            )
        )

        if telegram_user_id:
            query = query.filter(Transaction.telegram_user_id == telegram_user_id)

        transactions = query.all()

        # Calculate totals
        total_amount = sum(t.amount for t in transactions)
        transaction_count = len(transactions)

        # Group by category
        by_category = {}
        for transaction in transactions:
            category_name = transaction.category.name if transaction.category else "Sin categoría"
            by_category[category_name] = by_category.get(category_name, 0) + transaction.amount

        # Group by payment method
        by_payment_method = {}
        for transaction in transactions:
            method = transaction.payment_method
            by_payment_method[method] = by_payment_method.get(method, 0) + transaction.amount

        # Daily totals within the period
        daily_totals = {}
        for transaction in transactions:
            date_key = transaction.transaction_date.strftime("%Y-%m-%d")
            daily_totals[date_key] = daily_totals.get(date_key, 0) + transaction.amount

        return TransactionSummary(
            total_amount=total_amount,
            transaction_count=transaction_count,
            period_start=start_date,
            period_end=end_date,
            by_category=by_category,
            by_payment_method=by_payment_method,
            daily_totals=daily_totals
        )

    async def get_optimized_balance(
        self,
        start_date: datetime,
        telegram_user_id: Optional[int] = None
    ) -> dict:
        """Get optimized balance calculation using database aggregations"""

        # Build base query
        query = self.db.query(Transaction).filter(
            Transaction.transaction_date >= start_date
        )

        if telegram_user_id:
            query = query.filter(Transaction.telegram_user_id == telegram_user_id)

        # Calculate total expenses and count in one query
        totals = query.with_entities(
            func.sum(Transaction.amount).label('total_expenses'),
            func.count(Transaction.id).label('transaction_count')
        ).first()

        total_expenses = float(totals.total_expenses or 0)
        transaction_count = int(totals.transaction_count or 0)

        # Calculate daily average
        days_diff = (datetime.now() - start_date).days + 1
        daily_average = total_expenses / days_diff if days_diff > 0 else 0

        # Get top categories with aggregation
        category_query = query.join(Category, Transaction.category_id == Category.id, isouter=True)\
            .with_entities(
                func.coalesce(Category.name, 'Sin categoría').label('category_name'),
                func.sum(Transaction.amount).label('category_total')
            )\
            .group_by(func.coalesce(Category.name, 'Sin categoría'))\
            .order_by(func.sum(Transaction.amount).desc())\
            .limit(5)

        top_categories = [
            {"name": row.category_name, "total": float(row.category_total)}
            for row in category_query.all()
        ]

        # Get payment method breakdown
        payment_query = query.with_entities(
            Transaction.payment_method,
            func.sum(Transaction.amount).label('method_total')
        )\
        .group_by(Transaction.payment_method)\
        .order_by(func.sum(Transaction.amount).desc())

        payment_methods = {
            row.payment_method: float(row.method_total)
            for row in payment_query.all()
        }

        return {
            "total_expenses": total_expenses,
            "transaction_count": transaction_count,
            "daily_average": daily_average,
            "top_categories": top_categories,
            "payment_methods": payment_methods
        }

    async def _transaction_to_response(self, transaction: Transaction) -> TransactionResponse:
        """Convert Transaction model to TransactionResponse schema"""

        return TransactionResponse(
            id=transaction.id,
            amount=transaction.amount,
            description=transaction.description,
            payment_method=transaction.payment_method,
            transaction_date=transaction.transaction_date,
            location=transaction.location,
            category_id=transaction.category_id,
            telegram_message_id=transaction.telegram_message_id,
            telegram_user_id=transaction.telegram_user_id,
            ai_confidence=transaction.ai_confidence,
            ai_model_used=transaction.ai_model_used,
            original_text=transaction.original_text,
            is_validated=transaction.is_validated,
            is_correction=transaction.is_correction,
            corrected_transaction_id=transaction.corrected_transaction_id,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            # Category information
            category_name=transaction.category.name if transaction.category else None,
            category_color=transaction.category.color if transaction.category else None
        )