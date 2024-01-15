import uuid
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator
from pydantic_choices import choice
from typing_extensions import Annotated

from app.artefacts.schemas import ArtefactBase, ArtefactCreate, ArtefactPatch, ArtefactORM, ArtefactOut
from app.config import settings
from app.general.utils.AllOptional import AllOptional

from .models import Supporters
from app.config import settings

# Interlinker


Difficulties = choice(["very_easy", "easy", "medium", "difficult", "very_difficult"])

Targets = choice(["all", "all;pas", "all;pas;public_servants", "all;pas;politicians", "all;businesses", "all;businesses;smes", "all;businesses;freelancers", "all;businesses;large_companies", "all;businesses;private_non_profit",
                  "all;citizens", "all;citizens;potential_end_users", "all;citizens;expert_citizens", "all;research_organizations", "all;research_organizations;universities", "all;research_organizations;other_research_entities", 
                  "all;cs_project_leaders_and_initiators"])
InterlinkerTypes = choice(["enabling_services", "enabling_services;implementing_software_and_artifacts", "enabling_services;operation_services",
                          "enhancing_services", "enhancing_services;onboarding_services", "enhancing_services;followup_services", "enhancing_services:external_experts"])
AdministrativeScopes = choice(["eu", "national", "local"])

# kn
FormTypes = choice(["visual_template", "document_template", "canvas", "best_practices",
                   "guidelines", "checklist", "survey_template", "legal_agreement_template", "other"])
Formats = choice(["pdf", "editable_source_document",
                 "open_document", "structured_format"])

Themes = choice(["Introduction to CS", "Best Practices", "Project Management", 
                 "Research design and methods", "Engagement", "Co-creation", "Communication",
                 "Event planning", "CS stories", "Empowerment", "Data quality and standards",
                 "Instructions", "Link with formal education", "Regulations and ethics", "Impact",
                 "Evaluation of citizen science", "Project sustainability", "Transferability", "Reflections on science"])

class BaseInterlinkerBase(ArtefactBase):
    published: Optional[bool]
    difficulty: Difficulties
    targets: Optional[List[Targets]]

    types: Optional[List[InterlinkerTypes]]
    administrative_scopes: Optional[List[AdministrativeScopes]]
    # domain: Optional[str]
    process: Optional[str]

    form: Optional[FormTypes]
    format: Optional[Formats]
    is_sustainability_related: bool

    # GREENGAGE
    authors: Optional[List[str]]
    citizen_science_description_translations: Optional[dict]
    creation_date: Optional[date]
    doi: Optional[str]
    theme: Optional[Themes]
    publisher: Optional[str]
    external_link: Optional[str]

class BaseInterlinkerCreate(ArtefactCreate, BaseInterlinkerBase):
    logotype: Optional[str]
    snapshots: Optional[List[str]]
    instructions_translations: dict

class BaseInterlinkerPatch(ArtefactPatch):
    published: Optional[bool]
    difficulty: Optional[Difficulties]
    targets: Optional[List[Targets]]

    types: Optional[List[InterlinkerTypes]]
    administrative_scopes: Optional[List[AdministrativeScopes]]
    # domain: Optional[str]
    process: Optional[str]

    form: Optional[FormTypes]
    format: Optional[Formats]

    logotype: Optional[str]
    snapshots: Optional[List[str]]
    instructions_translations: Optional[dict]
    is_sustainability_related: Optional[bool]

    # GREENGAGE
    authors: Optional[List[str]]
    citizen_science_description_translations: Optional[dict]
    creation_date: Optional[date]
    doi: Optional[str]
    theme: Optional[Themes]
    publisher: Optional[str]
    external_link: Optional[str]

class BaseInterlinkerORM(ArtefactORM, BaseInterlinkerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    instructions: str

    citizen_science_description: Optional[str]

    class Config:
        orm_mode = True


class BaseInterlinkerOut(ArtefactOut, BaseInterlinkerORM):
    logotype_link: Optional[str]
    snapshots_links: Optional[List[str]]
    related_interlinkers: Optional[List[str]]

###

AuthMethods = choice(["header", "cookie"])

class SoftwareBaseInterlinkerBase(BaseInterlinkerBase):
    nature: Literal["softwareinterlinker"] = "softwareinterlinker"
    supported_by: List[Supporters]
    is_responsive: bool
    auth_method: AuthMethods

    # endpoint
    service_name: str
    domain: str
    path: str
    is_subdomain: bool
    api_path: str

    # capabilities
    instantiate: Optional[bool]
    clone: Optional[bool]
    view: Optional[bool]
    edit: Optional[bool]
    delete: Optional[bool]
    download: Optional[bool]
    preview: Optional[bool]
    open_in_modal: Optional[bool]
    shortcut: Optional[bool]


class SoftwareInterlinkerCreate(BaseInterlinkerCreate, SoftwareBaseInterlinkerBase):
    # capabilities translations
    instantiate_text_translations: Optional[dict]
    view_text_translations: Optional[dict]
    edit_text_translations: Optional[dict]
    delete_text_translations: Optional[dict]
    clone_text_translations: Optional[dict]
    download_text_translations: Optional[dict]
    preview_text_translations: Optional[dict]


class SoftwareInterlinkerPatch(BaseInterlinkerPatch):
    is_responsive:  Optional[bool]
    auth_method: Optional[AuthMethods]

    # endpoint
    service_name: Optional[str]
    domain: Optional[str]
    path: Optional[str]
    is_subdomain: Optional[bool]
    api_path: Optional[str]

    # capabilities
    instantiate: Optional[bool]
    clone: Optional[bool]
    view: Optional[bool]
    edit: Optional[bool]
    delete: Optional[bool]
    download: Optional[bool]
    preview: Optional[bool]
    open_in_modal: Optional[bool]
    shortcut: Optional[bool]
    instantiate_text_translations: Optional[dict]
    view_text_translations: Optional[dict]
    edit_text_translations: Optional[dict]
    delete_text_translations: Optional[dict]
    clone_text_translations: Optional[dict]
    download_text_translations: Optional[dict]
    preview_text_translations: Optional[dict]


class SoftwareBaseInterlinkerORM(BaseInterlinkerORM, SoftwareBaseInterlinkerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    instantiate_text: Optional[str]
    view_text: Optional[str]
    clone_text: Optional[str]
    edit_text: Optional[str]
    delete_text: Optional[str]
    preview_text: Optional[str]

    class Config:
        orm_mode = True


class SoftwareInterlinkerOut(BaseInterlinkerOut, SoftwareBaseInterlinkerORM):
    backend: Optional[str]

# class BasicSoftwareInterlinkerOut(PydanticBaseModel):
#     id: uuid.UUID
#     created_at: datetime
#     updated_at: Optional[datetime]
#     name: str
#     backend: Optional[str]
#     # status: str
#
#     class Config:
#         orm_mode = True
### 


class KnowledgeBaseInterlinkerBase(BaseInterlinkerBase):
    nature: Literal["knowledgeinterlinker"] = "knowledgeinterlinker"
    softwareinterlinker_id: uuid.UUID
    parent_id: Optional[uuid.UUID]


class KnowledgeInterlinkerCreate(BaseInterlinkerCreate, KnowledgeBaseInterlinkerBase):
    genesis_asset_id_translations: dict
    instructions_translations: dict


class KnowledgeInterlinkerPatch(BaseInterlinkerPatch):
    genesis_asset_id_translations: Optional[dict]
    instructions_translations: Optional[dict]


class KnowledgeBaseInterlinkerORM(BaseInterlinkerORM, KnowledgeBaseInterlinkerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    name_translations: dict
    genesis_asset_id_translations: dict
    genesis_asset_id: str

    class Config:
        orm_mode = True


class BasicKnowledgeInterlinker(BaseInterlinkerOut, KnowledgeBaseInterlinkerORM):
    link: str
    internal_link: str


class KnowledgeInterlinkerOut(BasicKnowledgeInterlinker, KnowledgeBaseInterlinkerORM):
    softwareinterlinker: Optional[SoftwareInterlinkerOut]
    children: List[BasicKnowledgeInterlinker]


### ExternalSoftwareInterlinker


class ExternalSoftwareBaseInterlinkerBase(BaseInterlinkerBase):
    nature: Literal["externalsoftwareinterlinker"] = "externalsoftwareinterlinker"    


class ExternalSoftwareInterlinkerCreate(BaseInterlinkerCreate, ExternalSoftwareBaseInterlinkerBase):
    uri_translations: dict
    asset_name_translations: Optional[dict]


class ExternalSoftwareInterlinkerPatch(BaseInterlinkerPatch):
    uri_translations: Optional[dict]
    asset_name_translations: Optional[dict]


class ExternalSoftwareBaseInterlinkerORM(BaseInterlinkerORM, ExternalSoftwareBaseInterlinkerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    uri: str
    asset_name: Optional[str]

    class Config:
        orm_mode = True


class BasicExternalSoftwareInterlinker(BaseInterlinkerOut, ExternalSoftwareBaseInterlinkerORM):
    pass


class ExternalSoftwareInterlinkerOut(BasicExternalSoftwareInterlinker, ExternalSoftwareBaseInterlinkerORM):
    pass



### ExternalKnowledgeInterlinker


class ExternalKnowledgeBaseInterlinkerBase(BaseInterlinkerBase):
    nature: Literal["externalknowledgeinterlinker"] = "externalknowledgeinterlinker"    


class ExternalKnowledgeInterlinkerCreate(BaseInterlinkerCreate, ExternalKnowledgeBaseInterlinkerBase):
    uri_translations: dict
    asset_name_translations: Optional[dict]


class ExternalKnowledgeInterlinkerPatch(BaseInterlinkerPatch):
    uri_translations: Optional[dict]
    asset_name_translations: Optional[dict]


class ExternalKnowledgeBaseInterlinkerORM(BaseInterlinkerORM, ExternalKnowledgeBaseInterlinkerBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime]

    uri: str
    asset_name: Optional[str]

    class Config:
        orm_mode = True


class BasicExternalKnowledgeInterlinker(BaseInterlinkerOut, ExternalKnowledgeBaseInterlinkerORM):
    pass


class ExternalKnowledgeInterlinkerOut(BasicExternalKnowledgeInterlinker, ExternalKnowledgeBaseInterlinkerORM):
    pass

###

InterlinkerCreate = Annotated[
    Union[SoftwareInterlinkerCreate, KnowledgeInterlinkerCreate, ExternalSoftwareInterlinkerCreate, ExternalKnowledgeInterlinkerCreate],
    Field(discriminator="nature"),
]

InterlinkerPatch = Annotated[
    Union[SoftwareInterlinkerPatch, KnowledgeInterlinkerPatch, ExternalSoftwareInterlinkerPatch, ExternalKnowledgeInterlinkerPatch],
    Field(discriminator="nature"),
]


class InterlinkerOut(BaseModel):
    __root__: Annotated[
        Union[SoftwareInterlinkerOut, KnowledgeInterlinkerOut, ExternalSoftwareInterlinkerOut, ExternalKnowledgeInterlinkerOut],
        Field(discriminator="nature"),
    ]
