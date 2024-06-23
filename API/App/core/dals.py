from typing import Union, List, Optional, BinaryIO
from uuid import UUID
from sqlalchemy.exc import IntegrityError
from fastapi import  HTTPException
from sqlalchemy import and_
from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
# from core.db import async_session
from models import User, Category, Allocation, ReferenceBook, BillToPay, Predictions
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError
from logging.config import dictConfig
import logging
from API.App.core.loging_config import LogConfig
from Algo.sber_algo import MainAllocationAssembler
from ML.predictions1 import MashineLearning
dictConfig(LogConfig().model_dump())
logger = logging.getLogger("washingtonsilver")

class UserDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, email: str, password: str) -> User:
        new_user = User(email=email,password=password)
        self.db_session.add(new_user)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_user

    async def delete_user(self, user_id: UUID) -> Union[UUID, None]:
        query = delete(User).where(User.user_id == user_id).returning(User.user_id)
        res = await self.db_session.execute(query)
        deleted_user_id_row = res.fetchone()
        if deleted_user_id_row:
            await self.db_session.commit()  
            return deleted_user_id_row[0]
        else:
            await self.db_session.rollback()  # Rollback in case of failure
            return None 

    async def get_user_by_id(self, user_id: UUID) -> Union[User, None]:
        query = select(User).where(User.user_id == user_id)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]
        
    async def get_user_by_email(self, email: str) -> Union[User, None]:
        query = select(User).where(User.email == email)
        res = await self.db_session.execute(query)
        user_row = res.fetchone()
        if user_row is not None:
            return user_row[0]
        
class CategoryDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def show_all_categories(self, user_id: UUID) -> List[Category]:
        query = select(Category).where(Category.user_id == user_id)
        result = await self.db_session.execute(query)
        categories = result.scalars().all()
        return categories

    async def create_category(self, name: str, user_id: UUID) -> Category:
        existing_category_query = select(Category).where(
            and_(Category.name == name,
            Category.user_id == user_id
        ))
        result = await self.db_session.execute(existing_category_query)
        existing_category = result.scalars().first()
        if existing_category:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        
        new_category = Category(name=name, user_id=user_id)
        self.db_session.add(new_category)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_category
    
    async def delete_category(self, category_name: str, user_id: UUID) -> Union[UUID, None]:
        query = delete(Category).where(
            and_(Category.user_id == user_id, Category.name == category_name)
            ).returning(Category.category_id)
        res = await self.db_session.execute(query)
        deleted_category_row = res.fetchone()
        if deleted_category_row:
            await self.db_session.commit()  
            return deleted_category_row[0]
        else:
            await self.db_session.rollback()  # Rollback in case of failure
            return None 

class AllocationDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def _check_allocation_objects(self, inspected_object_class, alloc_id: UUID, user_id: UUID) -> bool:
        query = select(inspected_object_class).where(
            and_(inspected_object_class.user_id == user_id,
                 inspected_object_class.alloc_id == alloc_id)
        )
        try:
            res = await self.db_session.execute(query)
            obj = res.scalar_one_or_none()
            logger.info(f"Validation object: Found !")
            return obj is not None
        except NoResultFound:
            logger.error(f"No result found for user_id: {user_id} and alloc_id: {alloc_id}")
            return False
        except SQLAlchemyError as e:
            logger.error(f"Database error occurred: {e}")
            return False
    
    async def _get_allocation_objects(self, inspected_object_class, alloc_id: UUID, user_id: UUID, fields: List[str]) -> dict[str, bytes]:
        columns = [getattr(inspected_object_class, field) for field in fields]
        query = select(*columns).where(
            and_(inspected_object_class.user_id == user_id,
                 inspected_object_class.alloc_id == alloc_id)
        )
        res = await self.db_session.execute(query)
        obj = res.fetchone()
        if obj is not None:
            result = {field: getattr(obj, field) for field in fields}
            return result
        return {}
    
        
    async def show_all_allocations(self, user_id: UUID, category: Optional[str] = None) -> List[Allocation]:
        query = select(Allocation).where(Allocation.user_id == user_id)
        if category:
            category_uuid = await self._get_category_by_name(category, user_id)
            query = select(Allocation).where(and_(Allocation.user_id == user_id, Allocation.category_id == category_uuid))
        result = await self.db_session.execute(query)
        allocations = result.scalars().all()
        return allocations
        
    async def create_allocation(self, name : str, category_name : str, user_id: UUID) -> Allocation:
        category_uuid = await self._get_category_by_name(category_name, user_id)
        existing_allocation_query = select(Category).where(
            and_(Allocation.name == name,
            Allocation.user_id == user_id,
            Allocation.category_id == category_uuid,
        ))
        result = await self.db_session.execute(existing_allocation_query)
        if result.scalars().first():
            raise HTTPException(status_code=400, detail="Allocation with this name and this category already exists")
        new_allocation = Allocation(name=name, category_id=category_uuid, user_id=user_id)
        self.db_session.add(new_allocation)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_allocation
    
    async def _get_category_by_name(self, name: str, user_id : UUID) -> Union[UUID, None]:
        query = select(Category).where(
            and_(Category.name == name, Category.user_id == user_id))
        res = await self.db_session.execute(query)
        category = res.scalars().first()
        try:
            return category.category_id
        except Exception:
            return None
        
    async def _get_category_by_id(self, category_id: UUID, user_id : UUID) -> Union[UUID, None]:
        query = select(Category).where(
            and_(Category.category_id == category_id, Category.user_id == user_id))
        res = await self.db_session.execute(query)
        category = res.scalars().first()
        try:
            return category.name
        except Exception:
            return None
        
    async def delete_allocation(self, allocation_name: str, category_name: str, user_id: UUID) -> Union[UUID, None]:
        query = delete(Allocation).where(
            and_(Allocation.user_id == user_id,
                 Allocation.name == allocation_name, 
                 Allocation.category_id == await self._get_category_by_name(category_name, user_id))
            ).returning(Allocation.alloc_id)
        res = await self.db_session.execute(query)
        deleted_allocation_row = res.fetchone()
        if deleted_allocation_row:
            await self.db_session.commit()  
            return deleted_allocation_row[0]
        else:
            await self.db_session.rollback()  
            return None 
        
        
    async def delete_allocation_by_id(self, allocation_id: UUID, user_id: UUID) -> Union[UUID, None]:
        query = delete(Allocation).where(
            and_(Allocation.user_id == user_id,
                 Allocation.alloc_id == allocation_id
                 )).returning(Allocation.alloc_id)
        res = await self.db_session.execute(query)
        deleted_allocation_row = res.fetchone()
        if deleted_allocation_row:
            await self.db_session.commit()  
            return deleted_allocation_row[0]
        else:
            await self.db_session.rollback()  
            return None     
        
    #! Allocation main processing   
    async def validate_and_process_allocation(self, allocation_id : UUID, user_id : UUID, rules : dict):
        if (await self._check_allocation_objects(ReferenceBook, allocation_id, user_id) ==
            await self._check_allocation_objects(BillToPay, allocation_id, user_id)) == True:
            logger.info("Allocation validation sucsess")
            bills_dict = await self._get_allocation_objects(BillToPay, allocation_id, user_id, ["bills_to_pay",])
            # logger.debug(f"Bills dict - {bills_dict}")
            reference_dict = await self._get_allocation_objects(ReferenceBook, allocation_id, user_id, ["contracts", "codes", "fixedassets", "building_squares", "contracts_to_building"])
            logger.info(f"Allocation items: Getted!!!")
            allocation_assembler = MainAllocationAssembler(bills_dict, reference_dict, rules)
            await allocation_assembler.async_init()
            logger.info("ALLOCATION ASSEMBLER INITIALIZED")
            csv_binary, xlsx_binary = await allocation_assembler.main()
            await self._write_allocation_results(allocation_id, user_id, csv_binary, xlsx_binary)
        else:
            raise HTTPException(status_code=400, detail="Required object or objects are missing")
        
    async def _write_allocation_results(self, allocation_id : UUID, user_id : UUID, csv_binary : BinaryIO, xlsx_binary : BinaryIO):
        query = select(Allocation).where(
            and_(Allocation.user_id == user_id,
                Allocation.alloc_id == allocation_id)
        )
        res = await self.db_session.execute(query)
        alloc_to_modify = res.scalar_one()
        alloc_to_modify.alloc_result_csv = csv_binary
        alloc_to_modify.alloc_result_xlsx = xlsx_binary
        await self.db_session.commit()
        
    async def download_allocation_content(self, allocation_id : UUID, user_id : UUID, xlsx_or_csv : bool):
        query = select(Allocation).where(
            and_(Allocation.user_id == user_id,
                Allocation.alloc_id == allocation_id)
        )
        res = await self.db_session.execute(query)
        file_data = res.scalar_one_or_none()
        
        if file_data is None:
            raise HTTPException(status_code=404, detail="Allocation not found")
        
        field = 'alloc_result_csv' if xlsx_or_csv else 'alloc_result_xlsx'
        if not hasattr(file_data, field):
            raise HTTPException(status_code=400, detail="Invalid field name")
        
        file_content = getattr(file_data, field)
        if file_content is None:
            raise HTTPException(status_code=404, detail="File content not found in the specified field")
        return file_content
        
    

class ReferenceDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def delete_referencebooks(self, ref_id: UUID, user_id: UUID) -> Union[UUID, None]:
        query = delete(ReferenceBook).where(
            and_(ReferenceBook.user_id == user_id,
                 ReferenceBook.ref_id == ref_id)
            ).returning(ReferenceBook.ref_id)
        res = await self.db_session.execute(query)
        deleted_row = res.fetchone()
        if deleted_row:
            await self.db_session.commit()  
            return deleted_row[0]
        else:
            await self.db_session.rollback()  # Rollback in case of failure
            return None 
    
    async def _create_referencebook(self, allocation_id : UUID, user_id: UUID, files : dict) -> ReferenceBook:
        if await self.is_reference_exist(allocation_id=allocation_id, user_id=user_id,):
            raise HTTPException(status_code=400, detail="The referencebooks already created for this allocation")
        new_refbook = ReferenceBook(
            user_id=user_id,
            alloc_id=allocation_id,
            contracts=files.get("contacts"),
            codes=files.get("codes"),
            fixedassets=files.get("fixedassets"),
            building_squares=files.get("building_squares"),
            contracts_to_building=files.get("contracts_to_building"),
        )
        self.db_session.add(new_refbook)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_refbook
    
    async def is_reference_exist(self, allocation_id: UUID, user_id: UUID) -> bool:
        query = select(ReferenceBook).where(
            and_(ReferenceBook.alloc_id == allocation_id,
            ReferenceBook.user_id == user_id
        ))
        res = await self.db_session.execute(query)
        if res.scalars().first():
            logger.warning(f"Reference found for allocation_id: {allocation_id} and user_id: {user_id}")
            return True
        else:
            logger.info(f"No reference found for allocation_id: {allocation_id} and user_id: {user_id}")
            return False
        
class BillDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def delete_bill(self, bill_id: UUID, user_id: UUID) -> Union[UUID, None]:
        query = delete(BillToPay).where(
            and_(BillToPay.user_id == user_id,
                 BillToPay.bill_id == bill_id)
            ).returning(BillToPay.bill_id)
        res = await self.db_session.execute(query)
        deleted_row = res.fetchone()
        if deleted_row:
            await self.db_session.commit()  
            return deleted_row[0]
        else:
            await self.db_session.rollback()  # Rollback in case of failure
            return None 
    
    async def _create_bill(self, allocation_id : UUID, user_id: UUID, files : dict) -> ReferenceBook:
        if await self.is_bill_exist(allocation_id=allocation_id, user_id=user_id,):
            raise HTTPException(status_code=400, detail="The bill already created for this allocation")
        new_bill = BillToPay(
            user_id=user_id,
            alloc_id=allocation_id,
            bills_to_pay=files.get("bills_to_pay")
        )
        self.db_session.add(new_bill)
        try:
            await self.db_session.flush()
        except IntegrityError:
            await self.db_session.rollback()
            raise
        return new_bill
    
    async def is_bill_exist(self, allocation_id: UUID, user_id: UUID) -> bool:
        query = select(BillToPay).where(
            and_(BillToPay.alloc_id == allocation_id,
            BillToPay.user_id == user_id
        ))
        res = await self.db_session.execute(query)
        if res.scalars().first():
            logger.warning(f"Reference found for allocation_id: {allocation_id} and user_id: {user_id}")
            return True
        else:
            logger.info(f"No reference found for allocation_id: {allocation_id} and user_id: {user_id}")
            return False
        

class PredictionDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        
    async def full_text_search(self, content : str, search_atribute : str, allocation_id : UUID, user_id: UUID):
        await self.db_session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))    
        try:
            q = text(f"""
            SELECT DISTINCT t."{search_atribute}", similarity(t."{search_atribute}"::text, '{content}') AS sim
            FROM "prediction_files" t 
            WHERE t."{search_atribute}" ILIKE :content
            AND t."alloc_id" = :alloc_id
            AND t."user_id" = :user_id
            ORDER BY sim DESC
            LIMIT 10;
            """)
            
            logging.info(f"Executing query: {q}")
            logging.info(f"With parameters: content='%{content}%', content_raw='{content}', alloc_id='{allocation_id}', user_id='{user_id}'")
            
            result = await self.db_session.execute(q, {
                'content': f'%{content}%',
                'content_raw': content,
                'alloc_id': str(allocation_id),
                'user_id': str(user_id)
            })
            
            res = result.fetchall()
            return [res[c][0] for c in range(len(res))]
            
        except Exception as e:
            logger.info("Similarities not find: ", e)
            
            fallback_query = text(f"""
                SELECT DISTINCT t."{search_atribute}"
                FROM "prediction_files" t
                WHERE t."alloc_id" = :alloc_id
                  AND t."user_id" = :user_id
                LIMIT 10;
                """)
                
            logging.warning(f"Executing fallback query: {fallback_query}")
            logging.warning(f"With parameters: alloc_id='{allocation_id}', user_id='{user_id}'")
            
            fallback_result = await self.db_session.execute(fallback_query, {
                'alloc_id': str(allocation_id),
                'user_id': str(user_id)
            })
            
            res = fallback_result.fetchall()  
            return [res[c][0] for c in range(len(res))]
    
        
        
    async def _is_ready_for_prediction(self, allocation_id : UUID, user_id: UUID) -> Union[bool, HTTPException]:
        query = select(Allocation).where(
            and_(Allocation.alloc_id == allocation_id,
            Allocation.user_id == user_id
        ))
        res = await self.db_session.execute(query)
        allocation = res.scalars().first()
        if allocation.alloc_result_csv != None and allocation.alloc_result_xlsx != None:
            return True
        else:
            raise HTTPException(status_code=404, detail="Allocation results aren't found")
        
    
    async def _get_allocation_xlsx_result(self, allocation_id : UUID, user_id: UUID) -> Union[BinaryIO, HTTPException]:
        query = select(Allocation).where(
            and_(Allocation.alloc_id == allocation_id,
            Allocation.user_id == user_id
        ))
        res = await self.db_session.execute(query)
        allocation = res.scalars().first()
        try:
            return allocation.alloc_result_xlsx
        except Exception as e:
            return HTTPException(status_code=500, detail=f"Something went wrong {e}")
        
        
        
    #! Predict core integration
    async def start_drediction(self, allocation_id : UUID, user_id: UUID):
        if await self._is_ready_for_prediction(allocation_id=allocation_id, user_id=user_id):
            binary_allocation_result = await self._get_allocation_xlsx_result(allocation_id=allocation_id, user_id=user_id)
            ml_instance = MashineLearning(binary_data=binary_allocation_result)
            ml_instance.main()
            predicted_data = ml_instance.get_all_data()
            for row in predicted_data:
                prediction_record = Predictions(
                user_id=user_id,
                alloc_id=allocation_id,
                time_period=row[0],
                building=row[2],
                price=row[1],
                main_ledger_id=str(row[5]),
                fixed_assets_id=str(row[4]),
                fixed_assets_class=str(row[3])
                )
                self.db_session.add(prediction_record)
            try:
                await self.db_session.flush()
            except IntegrityError:
                await self.db_session.rollback()
    
    async def search_for_predictions(self, allocation_id : UUID, user_id: UUID, searchable_atribute:str, searchable_value:str, months:int):
        query = select(Predictions).where(
                    and_(
                        Predictions.alloc_id == allocation_id,
                        Predictions.user_id == user_id,
                        getattr(Predictions, searchable_atribute) == searchable_value
                    )
                )
        result = await self.db_session.execute(query)
        records = result.scalars().all()
        return records
    
    
        # # filtered_records = []
        # # for record in records:
        # #     if hasattr(record, 'time_period'):
        # #         # Assume time_period is a datetime field
        # #         start_date = record.time_period
        # #         end_date = start_date + timedelta(days=30*months)
        # #         if record.time_period <= end_date:
        # #             filtered_records.append(record)
        # # return filtered_records
        # # query = select(Allocation).where(Allocation.user_id == user_id)
        # # if category:
        # #     category_uuid = await self._get_category_by_name(category, user_id)
        # #     query = select(Allocation).where(and_(Allocation.user_id == user_id, Allocation.category_id == category_uuid))
        # result = await self.db_session.execute(query)
        # allocations = result.scalars().all()
        # return allocations