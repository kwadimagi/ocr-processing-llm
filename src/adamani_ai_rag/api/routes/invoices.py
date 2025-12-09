
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from ...config import get_settings
from ..dependencies import get_db
from ...database.models import Invoice, User
from ...auth import current_active_user
from ...utils.logger import setup_logger, get_logger

settings = get_settings()
setup_logger(settings.log_level)
logger = get_logger()

router = APIRouter(tags=["invoices"])

class InvoiceUpdate(BaseModel):
    vendor_name: Optional[str] = None
    invoice_number: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None

@router.get("/invoices")
async def get_user_invoices(
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):

    # ✅ FETCH INVOICES
    logger.info(f"📊 Fetching invoices for user: {user.email}")
    query = (
        select(Invoice)
        .where(Invoice.user_id == user.id)
        .order_by(Invoice.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    invoices = result.scalars().all()

    logger.info(f"✅ Returning {len(invoices)} invoices for user {user.email}")

    return [
        {
            "id": str(inv.id),
            "vendor_name": inv.vendor_name,
            "invoice_number": inv.invoice_number,
            "total_amount": inv.total_amount,
            "currency": inv.currency,
            "invoice_date": inv.invoice_date.isoformat(),
            "due_date": inv.due_date.isoformat() if inv.due_date else None,
            "status": "paid" if inv.due_date and inv.due_date < datetime.utcnow() else "unpaid"
        }
        for inv in invoices
    ]

@router.put("/invoices/{invoice_id}")
async def update_invoice(
    invoice_id: str,
    update_data: InvoiceUpdate,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"✏️ Attempting to update invoice {invoice_id} for user {user.email}")

    query = select(Invoice).where(
        Invoice.id == invoice_id,
        Invoice.user_id == user.id
    )
    result = await db.execute(query)
    invoice = result.scalar_one_or_none()

    if not invoice:
        logger.warning(f"❌ Invoice {invoice_id} not found or unauthorized")
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Update fields if provided
    if update_data.vendor_name is not None:
        invoice.vendor_name = update_data.vendor_name
    if update_data.invoice_number is not None:
        invoice.invoice_number = update_data.invoice_number
    if update_data.total_amount is not None:
        invoice.total_amount = update_data.total_amount
    if update_data.currency is not None:
        invoice.currency = update_data.currency
    if update_data.invoice_date is not None:
        invoice.invoice_date = datetime.fromisoformat(update_data.invoice_date.replace('Z', '+00:00'))
    if update_data.due_date is not None:
        invoice.due_date = datetime.fromisoformat(update_data.due_date.replace('Z', '+00:00')) if update_data.due_date else None

    await db.commit()
    await db.refresh(invoice)

    logger.info(f"✅ Successfully updated invoice {invoice_id}")
    return {
        "id": str(invoice.id),
        "vendor_name": invoice.vendor_name,
        "invoice_number": invoice.invoice_number,
        "total_amount": invoice.total_amount,
        "currency": invoice.currency,
        "invoice_date": invoice.invoice_date.isoformat(),
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "status": "paid" if invoice.due_date and invoice.due_date < datetime.utcnow() else "unpaid"
    }

@router.delete("/invoices/{invoice_id}")
async def delete_invoice(
    invoice_id: str,
    user: User = Depends(current_active_user),
    db: AsyncSession = Depends(get_db)
):
    logger.info(f"🗑️ Attempting to delete invoice {invoice_id} for user {user.email}")

    query = select(Invoice).where(
        Invoice.id == invoice_id,
        Invoice.user_id == user.id
    )
    result = await db.execute(query)
    invoice = result.scalar_one_or_none()

    if not invoice:
        logger.warning(f"❌ Invoice {invoice_id} not found or unauthorized")
        raise HTTPException(status_code=404, detail="Invoice not found")

    await db.delete(invoice)
    await db.commit()

    logger.info(f"✅ Successfully deleted invoice {invoice_id}")
    return {"message": "Invoice deleted successfully"}