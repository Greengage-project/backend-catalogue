import json
from pathlib import Path
import os
import shutil
from slugify import slugify
from configuration import lang_keys
 
weblate_interlinkers = {}
weblate_problemprofiles = {}
weblate_schemas = {}

for lang_key in lang_keys:
    weblate_schemas[lang_key] = {}
    weblate_problemprofiles[lang_key] = {}
    weblate_interlinkers[lang_key] = {}
    


DELIMITER = ";"

def add_to_weblate(key: str, obj: dict, data: dict):
    for lang_code in lang_keys:
        ref = data.get("id", "").lower()
        for translatable_element in ["name_translations", "description_translations", "citizen_science_description_translations"]:
            if translatable_element in data:
                addon = translatable_element.replace("_translations", "")
                prefix = key + DELIMITER if key else ""
                key2 = prefix + ref + DELIMITER + addon
                value = data[translatable_element].get(lang_code, "")
                
                obj[lang_code][key2] = value

all_schemas = []

### PROBLEMPROFILES

with open("./problemprofiles/problemprofiles.json") as json_file:
    problemprofiles = json.load(json_file)
    for pp in problemprofiles:
        add_to_weblate("problemprofile", weblate_problemprofiles, pp)

### SCHEMAS

for schema_metadata_path in Path("./schemas").glob("**/metadata.json"):
    schema_data = None
    str_schema_metadata_path = str(schema_metadata_path)

    with open(str_schema_metadata_path) as json_file:
        schema_data = json.load(json_file)
        # set languages depending on current values of name and description
        # schema_data["languages"] = list(set(schema_data["name_translations"].keys()) & set(schema_data["description_translations"].keys()))
        # schema_data["environments"] = ["varam", "mef", "zgz"]

        schema_metadata = {**schema_data}

        parent = str(schema_metadata_path.parents[0])
        phases = os.listdir(parent + "/phases")

        schema_metadata["phases"] = []
        for phase_name in phases:
            path = parent + "/phases/" + phase_name

            phase = None
            with open(path) as phasefile:
                phase = json.load(phasefile)
                phase["id"] = "phase-" + slugify(phase["name_translations"]["en"],separator='_')

                last_objective = "" 
                for objective in phase["objectives"]:
                    
                    obj_prereqs = []
                    if last_objective:
                        obj_prereqs = [{
                            "item": last_objective,
                            "type": "previous"
                        }]                    
                    objective["prerequisites"] = obj_prereqs
                    last_objective = "objective-" + slugify(objective["name_translations"]["en"],separator='_')
                    objective["id"] = last_objective
                    
                    last_task = "" 
                    for task in objective["tasks"]:
                        
                        task_prereqs = []
                        if last_task:
                            task_prereqs = [{
                                "item": last_task,
                                "type": "previous"
                            }]
                        task["prerequisites"] = task_prereqs

                        last_task = "task-" + slugify(task["name_translations"]["en"],separator='_')
                        task["id"] = last_task
                        add_to_weblate(schema_metadata["id"] +  DELIMITER  + phase["id"] +  DELIMITER + objective["id"], weblate_schemas, task)
                    add_to_weblate(schema_metadata["id"] +  DELIMITER  + phase["id"], weblate_schemas, objective)
                add_to_weblate(schema_metadata["id"], weblate_schemas, phase)
            
            schema_metadata["phases"].append(phase)
            
            with open(path, "w") as json_file:
                json.dump(phase, json_file, indent=4) # important to not sort keys
        
        all_schemas.append(schema_metadata)
        add_to_weblate("", weblate_schemas, schema_metadata)

    with open(str_schema_metadata_path, "w") as json_file:
        json.dump(schema_data, json_file, indent=4, sort_keys=True)

### INTERLINKERS

for interlinker_metadata_path in Path("./interlinkers").glob("**/metadata.json"):
    with open(str(interlinker_metadata_path)) as json_file:
        interlinker_metadata = json.load(json_file)
        id = slugify(interlinker_metadata["name_translations"]["en"],separator='_').lower()
        # set as id the value of the name slugified
        interlinker_metadata["id"] = id
        # set languages depending on current values of name and description
        # interlinker_metadata["languages"] = list(set(interlinker_metadata["name_translations"].keys()) & set(interlinker_metadata["description_translations"].keys()))
        # interlinker_metadata["environments"] = ["varam", "mef", "zgz"]
        parent_folder = interlinker_metadata_path.parent.parent.name

        if parent_folder == "knowledge":
            add_to_weblate("knowledgeinterlinker", weblate_interlinkers, interlinker_metadata)
            interlinker_metadata["type"] = "knowledge"
        
        elif parent_folder == "software":
            add_to_weblate("softwareinterlinker", weblate_interlinkers, interlinker_metadata)
            interlinker_metadata["type"] = "software"
        
        elif parent_folder == "externalsoftware":
            interlinker_metadata["type"] = "software"
            add_to_weblate("externalsoftware", weblate_interlinkers, interlinker_metadata)
        
        elif parent_folder == "externalknowledge":
            interlinker_metadata["type"] = "knowledge"
            add_to_weblate("externalknowledge", weblate_interlinkers, interlinker_metadata)
    
    with open(str(interlinker_metadata_path), "w") as json_file:
        json.dump(interlinker_metadata, json_file, indent=4, sort_keys=True)

### DUMP ALL.JSON

with open(f"schemas_DO_NOT_MODIFY.json", "w") as f:
    json.dump(all_schemas, f, indent=4, sort_keys=True)
    
### DUMP WEBLATE JSONS

def export(obj, file):
    for lang_key, data in obj.items():
        with open(f"./weblate/{lang_key}/{file}", "w") as f:
            json.dump(data, f, indent=4, sort_keys=True)

export(weblate_interlinkers, "interlinkers.json")
export(weblate_problemprofiles, "problemprofiles.json")
export(weblate_schemas, "schemas.json")