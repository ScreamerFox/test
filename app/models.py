import uuid
from enum import Enum
from decimal import Decimal


from pydantic import BaseModel, condecimal
from sqlalchemy import UUID, DECIMAL
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

# Модель SQLAlchemy
class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    balance: Mapped[Decimal] = mapped_column(DECIMAL(30, 2), default=0)

    class Config:
        arbitrary_types_allowed = True


# Модель Pydantic для создания
class WalletCreate(BaseModel):
    balance: Decimal

    class Config:
        arbitrary_types_allowed = True

# Pydantic модель операции
class OperationType(str, Enum):
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"

    class Config:
        arbitrary_types_allowed = True

class WalletResponse(BaseModel):
    id: uuid.UUID
    balance: Decimal

    class Config:
        arbitrary_types_allowed = True


class WalletOperation(BaseModel):
    operationType: OperationType
    amount: condecimal(gt=0, decimal_places=2)

    class Config:
        arbitrary_types_allowed = True
