from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.general.utils.CRUDBase import CRUDBase

from .models import TreeItemMetadata
from .schemas import TreeItemCreate, TreeItemPatch
import uuid
from app.problemprofiles.crud import exportCrud as problemProfilesCrud


def recursive_check(id, obj):
    if hasattr(obj, "prerequisites"):
        for pre in obj.prerequisites:
            if id == pre.id:
                raise Exception("Circular prerequisite")
            return recursive_check(id, pre)
    return


class CRUDTreeItemMetadata(CRUDBase[TreeItemMetadata, TreeItemCreate, TreeItemPatch]):
    async def get_by_names(self, db: Session, name_translations: str, parent_id: uuid.UUID = None, coproductionschema_id: uuid.UUID = None) -> Optional[TreeItemMetadata]:
        queries = []
        if coproductionschema_id:
            queries.append(TreeItemMetadata.coproductionschema_id == coproductionschema_id)
        if parent_id:
            queries.append(TreeItemMetadata.parent_id == parent_id)
        return db.query(TreeItemMetadata).filter(
            and_(
                or_(
                    TreeItemMetadata.name_translations["en"] == name_translations["en"],
                    TreeItemMetadata.name_translations["es"] == name_translations["es"],
                    TreeItemMetadata.name_translations["it"] == name_translations["it"],
                    TreeItemMetadata.name_translations["lv"] == name_translations["lv"],
                    # TreeItemMetadata.name_translations["nl"] == name_translations["nl"],
                    # TreeItemMetadata.name_translations["da"] == name_translations["da"],
                ),
                *queries
            )
        ).first()

    async def sync_prerequisites(self, db: Session, treeitem: TreeItemMetadata, prerequisites: list = [], commit: bool = True) -> TreeItemMetadata:
        # Gets a list of prerequisite ids and creates / removes the relations
        prs = [await self.get(db=db, id=id) for id in prerequisites]
        for pr in treeitem.prerequisites:
            if pr not in prs:
                treeitem.prerequisites.remove(pr)
        for pr in prs:
            if pr not in treeitem.prerequisites:
                treeitem.prerequisites.append(pr)
        if commit:
            db.commit()
            db.refresh(treeitem)
        return treeitem

    async def clear_prerequisites(self, db: Session, treeitem: TreeItemMetadata, commit: bool = True) -> TreeItemMetadata:
        for pr in treeitem.prerequisites:
            treeitem.prerequisites.remove(pr)
        if commit:
            db.commit()
            db.refresh(treeitem)
        return treeitem

    async def delete_prerequisite(self, db: Session, treeitem: TreeItemMetadata, prerequisite: TreeItemMetadata, commit: bool = True) -> TreeItemMetadata:
        treeitem.prerequisites.remove(prerequisite)
        if commit:
            db.commit()
            db.refresh(treeitem)
        return treeitem

    async def add_prerequisite(self, db: Session, treeitem: TreeItemMetadata, prerequisite: TreeItemMetadata, commit: bool = True) -> TreeItemMetadata:
        if treeitem == prerequisite:
            raise Exception("Same object")

        recursive_check(treeitem.id, prerequisite)
        treeitem.prerequisites.append(prerequisite)
        if commit:
            db.commit()
            db.refresh(treeitem)
        return treeitem

    # PROBLEMPROFILES

    async def sync_problemprofiles(self, db: Session, treeitem: TreeItemMetadata, problemprofiles: list = [], commit: bool = True) -> TreeItemMetadata:
        # Gets a list of problemprofile ids and creates / removes the relations
        pps = [await problemProfilesCrud.get(db=db, id=id) for id in problemprofiles]
        for pp in treeitem.problemprofiles:
            if pp not in problemprofiles:
                treeitem.problemprofiles.remove(pp)
        for pp in pps:
            if pp not in treeitem.problemprofiles:
                treeitem.problemprofiles.append(pp)
        if commit:
            db.commit()
            db.refresh(treeitem)
        return treeitem

    async def delete_problemprofile(self, db: Session, treeitem: TreeItemMetadata, problemprofile: TreeItemMetadata, commit: bool = True) -> TreeItemMetadata:
        treeitem.problemprofiles.remove(problemprofile)
        if commit:
            db.commit()
            db.refresh(treeitem)
        return treeitem

    async def add_problemprofile(self, db: Session, treeitem: TreeItemMetadata, problemprofile: TreeItemMetadata, commit: bool = True) -> TreeItemMetadata:
        if treeitem == problemprofile:
            raise Exception("Same object")
        treeitem.problemprofiles.append(problemprofile)
        if commit:
            db.commit()
            db.refresh(treeitem)
        return treeitem

    # CRUD Permissions
    def can_create(self, user):
        return True

    def can_list(self, user):
        return True

    def can_read(self, user, object):
        return True

    def can_update(self, user, object):
        return True

    def can_remove(self, user, object):
        return True


exportCrud = CRUDTreeItemMetadata(TreeItemMetadata, logByDefault=True)
