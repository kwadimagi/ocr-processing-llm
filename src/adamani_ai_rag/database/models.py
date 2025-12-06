"""Database models for users, organizations, and documents."""
from datetime import datetime
from typing import Optional
import uuid

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, BigInteger, Integer, Text, Float
from sqlalchemy.dialects.postgresql import UUID,JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .base import Base

class User(SQLAlchemyBaseUserTableUUID, Base):
    """User model with FastAPI-Users integration."""
    __tablename__ = "users"

    # FastAPI-Users provides: id, email, hashed_password, is_active, is_superuser, is_verified
    full_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    owned_organizations = relationship(
        "Organization", back_populates="owner", foreign_keys="Organization.owner_id"
    )
    organization_memberships = relationship(
        "OrganizationMember", back_populates="user", cascade="all, delete-orphan"
    )
    documents = relationship("Document", back_populates="user")
    
    invoices = relationship("Invoice", back_populates="user")

class Organization(Base):
    """Organization (workspace/tenant) model."""
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    plan_tier: Mapped[str] = mapped_column(String(50), default="free")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Relationships
    owner = relationship("User", back_populates="owned_organizations", foreign_keys=[owner_id])
    members = relationship("OrganizationMember", back_populates="organization", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="organization", cascade="all, delete-orphan")


class OrganizationMember(Base):
    """Organization membership (many-to-many user-organization)."""
    __tablename__ = "organization_members"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), primary_key=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(50), default="member")
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="members")
    user = relationship("User", back_populates="organization_memberships")


class Document(Base):
    """Document model with organization isolation."""
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    file_size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    file_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="processing")
    chunks_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="documents")
    user = relationship("User", back_populates="documents")



class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_name = Column(String, nullable=False)
    vendor_address = Column(Text, nullable=True)
    invoice_number = Column(String, nullable=False, index=True)
    invoice_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=True)
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=True)
    currency = Column(String(3), default="USD", nullable=False)
    line_items = Column(JSONB, nullable=False, default=list)  # Store as JSON
    file_path = Column(String, nullable=True)  # Original file path
    created_at = Column(DateTime, default=datetime.utcnow)

    # Optional: link to user/org
    # 🔑 Add user association
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Optional: relationship (for ORM queries)
    user = relationship("User", back_populates="invoices")