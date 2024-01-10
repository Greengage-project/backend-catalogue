from enum import Enum
from typing import Dict, Union

from interlinkers.base import Difficulties, InterlinkerSchema, Licences
from pydantic import FilePath, HttpUrl, conlist


class SoftwareInterlinkers(Enum):
    googledrive = "googledrive"
    surveyeditor = "surveyeditor"
    ceditor = "ceditor"
    externalresourcemanager = "externalresourcemanager"


class Schema(InterlinkerSchema):
    # language: str

    softwareinterlinker: SoftwareInterlinkers
    file_translations:  Dict[str,  FilePath]
