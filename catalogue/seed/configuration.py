from enum import Enum


class Environments(Enum):
    varam = "varam"
    mef = "mef"
    zgz = "zgz"


class Languages(Enum):
    en = "en"
    es = "es"
    lv = "lv"
    it = "it"
    nl = "nl"
    dk = "dk"


lang_keys = [e.value for e in Languages]
