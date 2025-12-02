"""Organization service for managing workspaces."""
import uuid
import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..database.models import Organization, OrganizationMember, User
from ..utils.logger import get_logger

logger = get_logger()


class OrganizationService:
    """Service for managing organizations and memberships."""

    def __init__(self, session: AsyncSession):
        """Initialize organization service.

        Args:
            session: Database session
        """
        self.session = session

    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from organization name.

        Args:
            name: Organization name

        Returns:
            URL-safe slug
        """
        # Convert to lowercase and replace spaces with hyphens
        slug = name.lower().strip()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
        slug = re.sub(r'[-\s]+', '-', slug)    # Replace spaces/multiple hyphens

        # Add random suffix to ensure uniqueness
        suffix = str(uuid.uuid4())[:8]
        return f"{slug}-{suffix}"

    async def create_organization(
        self,
        name: str,
        owner_id: uuid.UUID,
        plan_tier: str = "free"
    ) -> Organization:
        """Create a new organization.

        Args:
            name: Organization name
            owner_id: Owner user ID
            plan_tier: Subscription tier

        Returns:
            Created organization
        """
        slug = self._generate_slug(name)

        # Create organization
        org = Organization(
            name=name,
            slug=slug,
            owner_id=owner_id,
            plan_tier=plan_tier
        )

        self.session.add(org)
        await self.session.flush()  # Get ID without committing

        # Add owner as admin member
        member = OrganizationMember(
            organization_id=org.id,
            user_id=owner_id,
            role="admin"
        )

        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(org)

        logger.info(f"Created organization {org.id} for user {owner_id}")

        return org

    async def get_user_organization(self, user_id: uuid.UUID) -> Optional[Organization]:
        """Get user's primary organization.

        Args:
            user_id: User ID

        Returns:
            User's organization or None
        """
        query = (
            select(Organization)
            .join(OrganizationMember)
            .where(OrganizationMember.user_id == user_id)
            .limit(1)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add_member(
        self,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str = "member"
    ) -> OrganizationMember:
        """Add a member to organization.

        Args:
            organization_id: Organization ID
            user_id: User ID
            role: Member role (admin, member, viewer)

        Returns:
            Organization membership
        """
        member = OrganizationMember(
            organization_id=organization_id,
            user_id=user_id,
            role=role
        )

        self.session.add(member)
        await self.session.commit()

        logger.info(f"Added user {user_id} to organization {organization_id} as {role}")

        return member

    async def get_organization_members(
        self,
        organization_id: uuid.UUID
    ) -> list[User]:
        """Get all members of an organization.

        Args:
            organization_id: Organization ID

        Returns:
            List of users
        """
        query = (
            select(User)
            .join(OrganizationMember)
            .where(OrganizationMember.organization_id == organization_id)
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())
