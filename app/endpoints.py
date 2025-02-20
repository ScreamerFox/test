import uuid
import logging

from decimal import Decimal
from json import JSONDecodeError

from app.database import get_db
from app.models import Wallet, WalletOperation, OperationType
from app.log_app.logger_app import cof_logging

from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy import select, exc
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

logger = logging.getLogger(__name__)


# создание кошелька
@router.post('/wallets/create', tags=['Администрирование'], name='создание кошелька')
async def create_wallets(db: AsyncSession = Depends(get_db)):
    cof_logging(level=logging.INFO)
    try:
        new_wallet = Wallet(balance=0)
        db.add(new_wallet)
        await db.commit()
        logger.info(f"запись нового кошелька создана и добавлена в бд. ИД - {new_wallet.id}")
        return {"id": new_wallet.id, "balance": new_wallet.balance}
    except exc.SQLAlchemyError as e:
        logger.error(f"Ошибка при создании кошелька: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Ошибка базы данных при создании кошелька: {e}")
    except Exception as e:
        logger.error(f"Непредвиденная ошибка при создании кошелька: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


# получаем все кошельки
@router.get('/wallets/all', tags=['Получение данных'], name='все кошельки')
async def all_wall(db: AsyncSession = Depends(get_db)):
    cof_logging(level=logging.WARNING)
    try:
        result = await db.execute(select(Wallet))
        res = result.scalars().all()
        if not res:
            logger.info("Данные отсутствуют")
            raise HTTPException(status_code=404, detail="Данные отсутствуют")
        logger.info("Данные получены")
        return res
    except exc.SQLAlchemyError as e:
        logger.error(f"Ошибка получения данных: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Ошибка базы данных: {e}")


# кошелёк по uuid
@router.get('/wallets/{wall_id}', tags=['Получение данных'], name='один кошелёк')
async def get_wallet(wall_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    cof_logging(level=logging.WARNING)
    try:
        result = await db.execute(select(Wallet).where(Wallet.id == wall_id))
        wallet = result.scalar_one_or_none()
        if not wallet:
            logger.info("Кошелек не найден")
            raise HTTPException(status_code=404, detail="Кошелек не найден")
        logger.info("Кошелёк найден")
        return wallet
    except exc.SQLAlchemyError as e:
        logger.error(f"Ошибка получения данных: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(status_code=500,
                            detail=f"Ошибка базы данных: {e}")


# основная ручка, для снятия или пополнения кошелька
@router.post('/wallets/{wall_id}/operation', tags=['Обновления'], name='Изменение баланса')
async def update_wallet_balance(
        wall_id: uuid.UUID,
        operation: WalletOperation,
        db: AsyncSession = Depends(get_db)
):
    cof_logging(level=logging.WARNING)

    amount = operation.amount
    op_type = operation.operationType.lower()

    try:
        async with db.begin():
            wallet = await db.execute(select(Wallet).where(Wallet.id == wall_id).with_for_update())
            wallet = wallet.scalar_one_or_none()

            if not wallet:
                logger.error("Кошелек не найден")
                raise HTTPException(status_code=404, detail="Кошелек не найден")

            logger.info(f"Кошелек найден, ID - {wallet.id}")

            if op_type == 'deposit':
                wallet.balance += amount
                logger.info(f"Кошелёк |{wallet.id}| пополнен на - {amount}")
            elif op_type == 'withdraw':
                if wallet.balance < amount:
                    raise HTTPException(status_code=400,
                                        detail=f"Недостаточно средств, не хватает на балансе {amount - wallet.balance}")
                wallet.balance -= amount
                logger.info(f"С кошелька |{wallet.id}| снято - {amount}")

            await db.commit()
            logger.debug(f"операция с кошельком |{wallet.id}| подтверждена")
            return wallet

    except exc.SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Ошибка - {repr(e)}, произведён откат")
        raise HTTPException(status_code=500, detail="Ошибка базы данных")

    except Exception as e:
        await db.rollback()
        logger.error(f"Ошибка - {repr(e)}, произведён откат")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")