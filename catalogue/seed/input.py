import json
from pathlib import Path
from configuration import lang_keys

lang_keys = ["en", "es", "it", "lv", "nl", "da"]

interlinker_paths = {}
for interlinker_metadata_path in Path("./interlinkers").glob("**/metadata.json"):
    path = str(interlinker_metadata_path)
    with open(path) as interlinker_file:
        interlinker_data = json.load(interlinker_file)
        interlinker_paths[interlinker_data["id"]] = path

schema_paths = {}
for schema_metadata_path in Path("./schemas").glob("**/*.json"):
    path = str(schema_metadata_path)
    with open(path) as schema_file:
        schema_data = json.load(schema_file)
        if "id" in schema_data:
            # add also phase json files
            if "objectives" in schema_data:
                with open(str(schema_metadata_path.parent.parent) + "/metadata.json") as parent_file:
                    parent_data = json.load(parent_file)
                    schema_paths[parent_data["id"] + ";" + schema_data["id"]] = path
            else:
                schema_paths[schema_data["id"]] = path

def update_interlinker(interlinker_id, attribute_key, value):
    if not interlinker_id in interlinker_paths:
        return
    path = interlinker_paths[interlinker_id]
    with open(path) as interlinker_file:
        interlinker_data = json.load(interlinker_file)
        if interlinker_data["id"] == interlinker_id:
            if interlinker_data[attribute_key][lang_key] != value:
                print("Updating", interlinker_id, attribute_key)
                interlinker_data[attribute_key][lang_key] = value
                with open(path, "w") as interlinker_write_file:
                    json.dump(interlinker_data, interlinker_write_file, indent=4, sort_keys=True)

for lang_key in lang_keys:
    with open(f"./weblate/{lang_key}/interlinkers.json") as interlinkers_weblate_json_file:
        weblate_interlinkers_data : dict = json.load(interlinkers_weblate_json_file)
        for key, value in weblate_interlinkers_data.items():
            values = key.split(";")
            interlinker_type = values[0]
            interlinker_id = values[1]
            attribute = values[2]
            update_interlinker(interlinker_id=interlinker_id, attribute_key=attribute + "_translations", value=value)
            
    with open(f"./weblate/{lang_key}/schemas.json") as schemas_weblate_json_file:
        weblate_schemas_data : dict = json.load(schemas_weblate_json_file)
        for key, value in weblate_schemas_data.items():
            values = key.split(";")
            length = len(values)
            
            schema_id = values[0]
            if(length == 2):
                attribute = values[1]
                path = schema_paths[schema_id]

                with open(path) as json_file:
                    data = json.load(json_file)
                    data[attribute + "_translations"][lang_key] = value
                with open(path, "w") as schema_write_file:
                    json.dump(data, schema_write_file, indent=4)

            elif(length == 3):
                phase_id = values[1]
                attribute = values[2]

                path = schema_paths[schema_id + ";" + phase_id]
                with open(path) as json_file:
                    data = json.load(json_file)
                    data[attribute + "_translations"][lang_key] = value
                with open(path, "w") as schema_write_file:
                    json.dump(data, schema_write_file, indent=4)

            elif(length == 4):
                phase_id = values[1]
                objective_id = values[2]
                attribute = values[3]

                path = schema_paths[schema_id + ";" + phase_id]
                with open(path) as json_file:
                    data = json.load(json_file)
                    for objective in data["objectives"]:
                        if objective["id"] == objective_id:
                            objective[attribute + "_translations"][lang_key] = value
                with open(path, "w") as schema_write_file:
                    json.dump(data, schema_write_file, indent=4)

            elif(length == 5):
                phase_id = values[1]
                objective_id = values[2]
                task_id = values[3]
                attribute = values[4]

                path = schema_paths[schema_id + ";" + phase_id]
                with open(path) as json_file:
                    data = json.load(json_file)
                    for objective in data["objectives"]:
                        if objective["id"] == objective_id:
                            for task in objective["tasks"]:
                                if task["id"] == task_id:
                                    task[attribute + "_translations"][lang_key] = value
                with open(path, "w") as schema_write_file:
                    json.dump(data, schema_write_file, indent=4)

    with open(f"./weblate/{lang_key}/problemprofiles.json") as problemprofiles_weblate_json_file:
        weblate_problemprofiles_data : dict = json.load(problemprofiles_weblate_json_file)
        for key, value in weblate_problemprofiles_data.items():
            values = key.split(";")
            problemprofile_id = values[1]
            attribute = values[2]
            
            path = "./problemprofiles/problemprofiles.json"
            with open(path) as problemprofiles_json_file:
                data = json.load(problemprofiles_json_file)
                for problemprofile in data:
                    if problemprofile["id"].lower() == problemprofile_id:
                        problemprofile[attribute + "_translations"][lang_key] = value
            with open(path, "w") as problemprofiles_write_file:
                json.dump(data, problemprofiles_write_file, indent=4, sort_keys=True)