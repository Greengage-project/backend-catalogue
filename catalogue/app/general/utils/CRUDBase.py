import logging
import uuid
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.general.db.base_class import Base
from app.messages import log
from app.config import settings

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
PatchSchemaType = TypeVar("PatchSchemaType", bound=BaseModel)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDBase(Generic[ModelType, CreateSchemaType, PatchSchemaType]):
    def __init__(self, model: Type[ModelType], logByDefault=False):
        """
        CRUD object with default methods to Create, Read, Patch, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.logByDefault = logByDefault
        self.modelName = model.__name__.upper()
        self.model = model

    async def get(self, db: Session, id: uuid.UUID) -> Optional[ModelType]:
        if obj := db.query(self.model).filter(self.model.id == id).first():
            await self.log_on_get(obj)
            return obj
        return

    async def get_by_name(self, db: Session, name: str) -> Optional[ModelType]:
        if obj := db.query(self.model).filter(self.model.name == name).first():
            await self.log_on_get(obj)
            return obj
        return

    async def get_by_name_translation(self, db: Session, name: str, language: str = settings.DEFAULT_LANGUAGE) -> Optional[ModelType]:
        if obj := db.query(self.model).filter(self.model.name_translations[language] == name).first():
            await self.log_on_get(obj)
            return obj
        return

    async def get_by_name_translations(self, db: Session, name_translations: str) -> Optional[ModelType]:
        return db.query(self.model).filter(
            or_(
                and_(self.model.name_translations["en"] != None, self.model.name_translations["en"] == name_translations["en"]),
                and_(self.model.name_translations["es"] != None, self.model.name_translations["es"] == name_translations["es"]),
                and_(self.model.name_translations["it"] != None, self.model.name_translations["it"] == name_translations["it"]),
                and_(self.model.name_translations["lv"] != None, self.model.name_translations["lv"] == name_translations["lv"]),
                and_(self.model.name_translations["nl"] != None, self.model.name_translations["nl"] == name_translations["nl"]),
                and_(self.model.name_translations["da"] != None, self.model.name_translations["da"] == name_translations["da"]),
            ),
        ).first()

    async def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).order_by(self.model.created_at.asc()).offset(skip).limit(limit).all()

    async def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        await self.log_on_create(db_obj)
        return db_obj

    async def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[PatchSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field) and value != getattr(db_obj, field):
                print("Updating", field)
                setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        await self.log_on_update(db_obj)
        return db_obj

    async def remove(self, db: Session, *, id: uuid.UUID) -> ModelType:
        obj = db.query(self.model).get(id)
        await self.log_on_remove(obj)
        db.delete(obj)
        db.commit()
        return obj

    # LOGS
    async def log_on_get(self, obj):
        # enriched : dict  = self.enrich_log_data(obj, {
        #     "action": "GET"
        # })
        # await log(enriched)
        pass

    async def log_on_create(self, obj):
        enriched: dict = self.enrich_log_data(obj, {
            "action": "CREATE"
        })
        await log(enriched)

    async def log_on_update(self, obj):
        enriched: dict = self.enrich_log_data(obj, {
            "action": "UPDATE"
        })
        await log(enriched)

    async def log_on_remove(self, obj):
        enriched: dict = self.enrich_log_data(obj, {
            "action": "DELETE"
        })
        await log(enriched)

    def enrich_log_data(self, obj, logData) -> dict:
        logData["model"] = self.modelName
        logData["object_id"] = obj.id
        return logData

    # CRUD Permissions

    def can_create(self, user):
        logger.warn("You need to override can_create of the crud")
        return True

    def can_list(self, user):
        logger.warn("You need to override can_list of the crud")
        return True

    def can_read(self, user, object):
        logger.warn("You need to override can_read of the crud")
        return True

    def can_update(self, user, object):
        logger.warn("You need to override can_update of the crud")
        return True

    def can_remove(self, user, object):
        logger.warn("You need to override can_remove of the crud")
        return True
