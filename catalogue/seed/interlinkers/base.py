from enum import Enum
from typing import Dict, List, Optional, Union

from slugify import slugify

from problemprofiles.problemprofiles import WithProblemProfiles
from pydantic import BaseModel, Extra, FilePath, HttpUrl, conlist, validator
from configuration import Languages, Environments
from datetime import datetime

# https://docs.google.com/spreadsheets/d/1tJ2BfX4EOdbBqEbrJWg8a3MENw13vYiPZM_S4wWWgWQ/edit#gid=0


class FormTypes(Enum):
    software = "software"
    visual_template = "visual_template"
    document_template = "document_template"
    canvas = "canvas"
    best_practices = "best_practices"
    guidelines = "guidelines"
    checklist = "checklist"
    survey_template = "survey_template"
    legal_agreement_template = "legal_agreement_template"
    other = "other"


class Formats(Enum):
    pdf = "pdf"
    editable_source_document = "editable_source_document"
    open_document = "open_document"
    structured_format = "structured_format"
    software = "sofware"
    collection = "collection"
    dataset = "dataset"
    event = "event"
    image = "image"
    text = "text"
    interactive_resource = "interactive_resource (website)"
    physical_object = "physical_object (hardware)"
    moving_image = "moving_image (video)"
    service = "service"
    sound = "sound"
    still_image = "still_image"


class Difficulties(Enum):
    very_easy = "very_easy"
    easy = "easy"
    medium = "medium"
    difficult = "difficult"
    very_difficult = "very_difficult"


class Licences(Enum):
    public_domain = "public_domain"
    permissive = "permissive"
    copyleft = "copyleft"
    non_commercial = "non_commercial"
    propietary = "propietary"


class Targets(Enum):
    all = "all"
    pas = "all;pas"
    public_servants = "all;pas;public_servants"
    politicians = "all;pas;politicians"
    businesses = "all;businesses"
    smes = "all;businesses;smes"
    freelancers = "all;businesses;freelancers"
    large_companies = "all;businesses;large_companies"
    private_non_profit = "all;businesses;private_non_profit"
    citizens = "all;citizens"
    potential_end_users = "all;citizens;potential_end_users"
    expert_citizens = "all;citizens;expert_citizens"
    cs_project_leaders_and_initiators = "all;cs_project_leaders_and_initiators"
    research_organizations = "all;research_organizations"
    universities = "all;research_organizations;universities"
    other_research_entities = "all;research_organizations;other_research_entities"

class ProblemProfiles(str):
    pass


class InterlinkerTypes(Enum):
    enabling = "enabling_services"
    implementation = "enabling_services;implementing_software_and_artifacts"
    operation = "enabling_services;operation_services"
    enhancing = "enhancing_services"
    onboarding = "enhancing_services;onboarding_services"
    followup = "enhancing_services;followup_services"
    external = "enhancing_services:external_experts"


class AdministrativeScopes(Enum):
    eu = "eu"
    national = "national"
    local = "local"


class Themes(Enum):
    introduction_to_cs = "Introduction to CS"
    best_practices = "Best Practices"
    project_management = "Project Management"
    research_design_and_methods = "Research design and methods"
    engagement = "Engagement"
    co_creation = "Co-creation"
    communication = "Communication"
    event_planning = "Event planning"
    cs_stories = "CS stories"
    empowerment = "Empowerment"
    data_quality_and_standards = "Data quality and standards"
    instructions = "Instructions"
    link_with_formal_education = "Link with formal education"
    regulations_and_ethics = "Regulations and ethics"
    impact = "Impact"
    evaluation_of_citizen_science = "Evaluation of citizen science"
    project_sustainability = "Project sustainability"
    transferability = "Transferability"
    reflections_on_science = "Reflections on science"


class InterlinkerSchema(WithProblemProfiles, extra=Extra.forbid):
    is_sustainability_related: bool
    name_translations: dict
    # FOR 1
    # A name for the INTERLINKER.
    # This input will be:
    # - Shown on the platform interface in the page showing the details of the INTERLINKER
    # - Used for searching/browsing the catalogue of INTERLINKERS by name

    description_translations: dict
    # FOR 1
    # Textual description of the INTERLINKER, its functionality, usage, etc.
    # This input will be:
    # - Shown on the platform interface in the page showing the details of the INTERLINKER

    constraints_and_limitations_translations: dict
    # FOR 1
    # Specific requirements and properties constraining the usage and exploitation of the INTERLINKER
    # This input will be:
    # - Shown to technical users of the platform to explain how the INTERLINKER can be used as a Building Block for Public Services
    # - (To be decided) Shown on the platform interface in the page showing the details of the INTERLINKER
    # - (To be decided) Used by the Wizard algorithms for intelligent filtering and recommendation

    regulations_and_standards_translations: Optional[dict]
    # FOR 1
    # Legal and technical context where the INTERLINKER operates, as a set of relevant, normative acts, policies, standards, and specification the INTERLINKER adheres to.
    # This input will be:
    # - Shown to technical users of the platform to explain how the INTERLINKER adheres to national and EU standards
    # - (To be decided) Shown on the platform interface in the page showing the details of the INTERLINKER
    # - (To be decided) Used by the Wizard algorithms for intelligent filtering and recommendation
    #
    # Possible values:
    # In the initial specification of INTERLINKERS this field will be defined as textual, to allow for more freedom in the description.
    # To be further evaluated which types of standard classifications will be used as id for a more constrained filling of this field.

    tags_translations: Dict[str,  conlist(str, min_items=1)]
    # FOR 1
    # Tags that can be used to characterize the INTERLINKER

    ## INTERLINKER SPECIFIC
    difficulty: Difficulties
    # FOR 1
    # Level of difficulty in using the tool

    targets: Optional[List[Targets]]
    # FOR 2
    # List of stakeholders, if applicable, that will be engaged in using this INTERLINKER.

    licence: Licences
    # FOR 1
    # Type of licences under which the INTERLINKER is usable.
    # The user should be provided with information that explains the meaning of the different licences, both for software and knowledge.

    problemprofiles: List[ProblemProfiles]
    # FOR 1
    # List of names of Problem Profiles associated to the INTERLINKER
    # This input will be:
    # - Shown on the platform interface in the page showing the details of the INTERLINKER
    # - Used by the Wizard algorithms for intelligent filtering and recommendation

    types: Optional[List[InterlinkerTypes]]
    # FOR 2
    # Either Enabling or Enhancing Service with the corresponding sub-classification.
    # This input will be:
    # - Used internally by the INTERLINK platform to describe how the INTERLINKER relates to the standard classifications introduced by the CEF Service Offering Canvas (SOC)

    administrative_scopes: Optional[List[AdministrativeScopes]]
    # FOR 2
    # This field describes the administrative context for which this INTERLINKER is particularly suitable.
    # Multiple values are possible:

    domain: Optional[str]
    # FOR 2
    # This field describes the Public Service application domain for which this INTERLINKER is particularly suitable.
    # Possible values should be taken from standard classifications of public services. (For example the Core Public Service Vocabulary Application Profile (CPSV-AP) developed within the ISA2 European initiative).

    process: Optional[str]
    # FOR 2
    # This field describes the governance model for which the INTERLINKER is particularly suitable.

    overview_text: Optional[dict]
    # FOR 2
    # Explanation of what is made available for user interaction.

    form: Optional[FormTypes]
    # FOR 1
    # Type of knowledge INTERLINKER: e.g., visual template, document template, canvas, best practices, guidelines, checklist, survey template, legal agreement template
    # This input will be:
    # - Shown on the platform interface in the page showing the details of the INTERLINKER

    format: Optional[Formats]
    # FOR 1 // COULD BE INFERED
    # Type of the format used to encode the knowledge of the INTERLINKER
    # This input will be:
    # - Shown on the platform interface in the page showing the details of the INTERLINKER

    instructions_translations:  Dict[str,  Union[HttpUrl, FilePath]]

    # AUTOMATICALLY GENERATED
    id: Optional[str]
    type: Optional[str]
    languages: Optional[List[Languages]]
    environments: Optional[List[Environments]]

    # EXTRA FOR GREENGAGE
    authors: Optional[List[str]]
    # List of authors of the INTERLINKER

    citizen_science_description_translations: Optional[dict]
    # Citizen science related description

    creation_date: Optional[datetime]
    # Creation date of the asset

    doi: Optional[str]
    # Digital Object Identifier of the asset. A unique alphanumeric string assigned to a digital object.

    themes: Optional[Themes]
    # List of themes or categories that the INTERLINKER is associated with.

    publisher: Optional[str]
    # Publishers of the asset