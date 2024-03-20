import asyncio
import json
import logging
import ntpath
import os
import shutil
from distutils.dir_util import copy_tree
from pathlib import Path

import requests
from slugify import slugify

from app import crud, models, schemas
from app.config import settings
from app.general.db.session import SessionLocal
from app.messages import set_logging_disabled

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def move_file(origin, destination):
    # print(f"Copying from {origin} to {destination}")
    shutil.copy(origin, destination)


def get_snapshots(origin, dest):
    # create directory in static for its files and clean if has contents
    static_path = Path(dest)
    shutil.rmtree(static_path, ignore_errors=True)
    static_path.mkdir(parents=True, exist_ok=True)

    # get snapshots folder content and move them to static folder
    snapshots_folder = str(origin) + "/snapshots"
    static_snapshots_folder = dest + "/snapshots"

    if os.path.isdir(snapshots_folder):
        fol = static_snapshots_folder.replace("/app", "")
        snapshots = [
            f"{fol}/{file}" for file in os.listdir(snapshots_folder) if file.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'))]
        copy_tree(snapshots_folder, static_snapshots_folder)

        # print(snapshots)
        return snapshots
    return []


def get_logotype(logotype_path, origin, dest):
    # create directory in static for its files and clean if has contents
    file_path = path_leaf(logotype_path)
    filename, file_extension = os.path.splitext(file_path)
    ori = str(origin) + "/" + file_path
    dst = f"{dest}/logotype{file_extension}"
    move_file(ori, dst)
    # print(dst)
    return dst.replace("/app", "")


async def create_interlinker(db, metadata_path, software=False, externalsoftware=False, knowledge=False, externalknowledge=False):
    error = False
    ####################
    # COMMON for all interlinker types
    ####################
    str_metadata_path = str(metadata_path)
    with open(str_metadata_path) as json_file:
        data = json.load(json_file)

    # get the english name of the interlinker for finding it
    name = data["name_translations"]["en"]
    print(f"\n{bcolors.OKBLUE}Processing {bcolors.ENDC}{bcolors.BOLD}{name}{bcolors.ENDC}")

    # get the existing interlinker
    existing_interlinker = await crud.interlinker.get_by_name(db=db, name=name)
    if (existing_interlinker):
        print(f"\t{bcolors.WARNING}Already in the database{bcolors.ENDC}. UPDATING")

    # Get the parent folder object where the metadata.json is located
    folder = metadata_path.parents[0]
    slug = slugify(name)
    str_static_path = f'/app/static/{slug}'

    # Copy the snapshots and the logotype
    data["snapshots"] = get_snapshots(folder, str_static_path)
    data["logotype"] = get_logotype(
        data["logotype"], folder, str_static_path) if "logotype" in data else None

    # Get the instructions file contents (normally is a README file, but it can be a pointer to a URI. 
    # In that case, the URI is stored, there is no need to read the content of the file)
    for LANGUAGE_KEY, FILE_NAME_OR_URL in data["instructions_translations"].items():
        if not "http" in FILE_NAME_OR_URL:
            filename = path_leaf(FILE_NAME_OR_URL)
            with open(str(folder) + "/" + filename, 'r') as f:
                data["instructions_translations"][LANGUAGE_KEY] = f.read()

    ###################################
    # ONLY FOR SOFTWARE INTERLINKERS
    ###################################

    if software:
        # set nature
        data["nature"] = "softwareinterlinker"
        data = {**data, **data["integration"]}
        data = {**data, **data["integration"]["capabilities"]}
        data = {**data, **data["integration"]["capabilities_translations"]}
        del data["integration"]

        # create interlinker
        if existing_interlinker:
            interlinker = await crud.interlinker.update(
                db=db,
                db_obj=existing_interlinker,
                obj_in=schemas.SoftwareInterlinkerPatch(**data),
            )
            print(f"\t{bcolors.OKGREEN}Updated successfully!{bcolors.ENDC}")
        else:
            interlinker = await crud.interlinker.create(
                db=db,
                interlinker=schemas.SoftwareInterlinkerCreate(**data),
            )
            print(f"\t{bcolors.OKGREEN}Created successfully!{bcolors.ENDC}")

    ###################################
    # ONLY FOR EXTERNAL KNOWLEDGE INTERLINKERS
    ###################################
    if externalknowledge:
        data["nature"] = "externalknowledgeinterlinker"

        if existing_interlinker:
            interlinker = await crud.interlinker.update(
                db=db,
                db_obj=existing_interlinker,
                obj_in=schemas.ExternalKnowledgeInterlinkerPatch(**data),
            )
            print(f"\t{bcolors.OKGREEN}Updated successfully!{bcolors.ENDC}")
        else:
            interlinker = await crud.interlinker.create(
                db=db,
                interlinker=schemas.ExternalKnowledgeInterlinkerCreate(**data),
            )
            print(f"\t{bcolors.OKGREEN}Created successfully!{bcolors.ENDC}")

    ###################################
    # ONLY FOR EXTERNAL SOFTWARE INTERLINKERS
    ###################################

    if externalsoftware:
        # set nature
        data["nature"] = "externalsoftwareinterlinker"

        if existing_interlinker:
            interlinker = await crud.interlinker.update(
                db=db,
                db_obj=existing_interlinker,
                obj_in=schemas.ExternalSoftwareInterlinkerPatch(**data),
            )
            print(f"\t{bcolors.OKGREEN}Updated successfully!{bcolors.ENDC}")
        else:
            interlinker = await crud.interlinker.create(
                db=db,
                interlinker=schemas.ExternalSoftwareInterlinkerCreate(**data),
            )
            print(f"\t{bcolors.OKGREEN}Created successfully!{bcolors.ENDC}")

    ###################################
    # ONLY FOR KNOWLEDGE INTERLINKERS
    ###################################
    # Knowledge interlinkers are the most complex type of interlinkers to be updated. As the knowledge interlinkers point to an asset managed by a software interlinkers,
    # there is no (or easy) way to know if the asset used to create the interlinker has changed.
    # For example, we are using a pptx to build the interlinker Business Model Canvas (check seed/interlinkers/knowledge/Business Model Canvas).
    # To "Update" them, we make a DELETE request to the interlinker (with the genesis asset id of the knowledge interlinker) and we create it again with the pptx in the folder.
    # This way, we do not care if it has changed or not. It is not the optimal way, but the easiest to maintain.

    if knowledge:
        existing_interlinker: models.KnowledgeInterlinker
        # get file contents in file and send to the software interlinker
        service = data["softwareinterlinker"]
        softwareinterlinker = await crud.interlinker.get_softwareinterlinker_by_service_name(db=db, service_name=service)
        if not softwareinterlinker:
            print(f"\t{bcolors.FAIL}there is no {service} softwareinterlinker{bcolors.ENDC}")
            return

        try:
            print(f"\tis {service} supported knowledge interlinker")

            genesis_asset_id_translations = {}
            for LANGUAGE_KEY, COMPLE_FILE_URL in data["file_translations"].items():
                # Get only the name of the file (we already know the folder where it is located)
                filename = path_leaf(COMPLE_FILE_URL)
                

                # Delete existent asset in the interlinker for the given language key
                if existing_interlinker:
                    existing_asset_id = getattr(existing_interlinker, "genesis_asset_id_translations", {}).get(LANGUAGE_KEY, None)
                    if existing_asset_id:
                        URL = f"http://{softwareinterlinker.service_name}{softwareinterlinker.api_path}/{existing_asset_id}"
                        response = requests.delete(URL, headers={
                            "Authorization": settings.BACKEND_SECRET
                        })
                        if (response.status_code < 200 or response.status_code >= 300) and response.status_code != 404:
                            raise Exception(response.json())

                # Create a new asset with the content of the file in file_translations
                short_filename, file_extension = os.path.splitext(filename)

                ## if the file is json, read the content and send it in post data as json
                if "json" in file_extension:
                    with open(str(folder) + "/" + filename, 'r') as f:
                        response = requests.post(
                            f"http://{service}/assets", data=f.read())
                
                ## if the file is a file (like pdf, pptx...), read the content and send it in post data as file
                else:
                    filedata = open(str(folder) + "/" + filename, "rb").read()
                    name_for_file = data["name_translations"][LANGUAGE_KEY]
                    files_data = {
                        'file': (name_for_file + file_extension, filedata)}
                    response = requests.post(
                        f"http://{service}/assets", files=files_data)

                if response.status_code < 200 or response.status_code >= 300:
                    raise Exception(response.json())
                
                response_data = response.json()
                genesis_asset_id_translations[LANGUAGE_KEY] = response_data["id"] if "id" in response_data else response_data["_id"]
                print(f"Asset for the {LANGUAGE_KEY} has been created and added into the genesis_asset_id_translations dict")

            # Last fields needed for the knowledge interlinker
            data["softwareinterlinker_id"] = softwareinterlinker.id
            data["genesis_asset_id_translations"] = genesis_asset_id_translations
            if existing_interlinker:
                interlinker: models.KnowledgeInterlinker = await crud.interlinker.update(
                    db=db,
                    db_obj=existing_interlinker,
                    obj_in=schemas.KnowledgeInterlinkerPatch(**data),
                )

                # Comprobation that the genesis asset ids have been updated
                if interlinker.genesis_asset_id_translations != genesis_asset_id_translations:
                    raise Exception(
                        f"{interlinker.genesis_asset_id_translations} not equal to {genesis_asset_id_translations}")
                print(f"\t{bcolors.OKGREEN}Updated successfully!{bcolors.ENDC}")
            else:
                interlinker: models.KnowledgeInterlinker = await crud.interlinker.create(
                    db=db,
                    interlinker=schemas.KnowledgeInterlinkerCreate(**data),
                )
                print(f"\t{bcolors.OKGREEN}Created successfully!{bcolors.ENDC}")

        except Exception as e:
            error = True
            print(f"\t{bcolors.FAIL}{str(e)}{bcolors.ENDC}")


async def create_problemprofile(db, problem):
    id = problem["id"]
    if pp := await crud.problemprofile.get(
        db=db,
        id=id
    ):
        print(f"\t{bcolors.WARNING}{id} already in the database{bcolors.ENDC}. UPDATING")
        await crud.problemprofile.update(
            db=db,
            db_obj=pp,
            obj_in=schemas.ProblemProfilePatch(**problem)
        )
        return
    await crud.problemprofile.create(
        db=db,
        obj_in=schemas.ProblemProfileCreate(**problem)
    )
    print(f"\t{bcolors.OKGREEN}Problem profile {id} created successfully!{bcolors.ENDC}")


async def create_coproductionschema(db, schema_data):
    name = schema_data["name_translations"]["en"]
    if (sc := await crud.coproductionschema.get_by_name(db=db, locale="en", name=name)):
        print(f"\t{bcolors.WARNING}{name} already in the database{bcolors.ENDC}. UPDATING")
        SCHEMA = await crud.coproductionschema.update(
            db=db,
            db_obj=sc,
            obj_in=schemas.CoproductionSchemaPatch(
                **schema_data, is_public=True
            )
        )
    else:
        SCHEMA = await crud.coproductionschema.create(
            db=db,
            obj_in=schemas.CoproductionSchemaCreate(
                **schema_data, is_public=True
            )
        )

    print(f"{bcolors.OKBLUE}## Processing {bcolors.ENDC}{name}")
    items_resume = {}

    phase_data: dict
    touched_phases = []
    for phase_data in schema_data["phases"]:
        if phase_in_db := await crud.treeitems.get_by_names(db=db, name_translations=phase_data["name_translations"], coproductionschema_id=SCHEMA.id):
            print(f"{bcolors.WARNING}Updating existing phase {phase_in_db.name}{bcolors.ENDC}")
            db_phase = await crud.treeitems.update(db=db, db_obj=phase_in_db, obj_in=schemas.TreeItemPatch(**phase_data))
        else:
            phase_name = phase_data.get("name_translations", {}).get("en", "undefined")
            print(f"{bcolors.OKGREEN}Creating {phase_name}{bcolors.ENDC}")
            db_phase = await crud.treeitems.create(
                db=db,
                obj_in=schemas.TreeItemCreate(
                    **phase_data,
                    coproductionschema_id=SCHEMA.id,
                    type=models.TreeItemTypes.phase
                )
            )
        touched_phases.append(db_phase)
        items_resume[phase_data["id"]] = {
            "db_id": db_phase.id,
            "prerequisites": phase_data.get("prerequisites", [])
        }

        objective_data: dict
        touched_objectives = []
        for objective_data in phase_data["objectives"]:
            if objective_in_db := await crud.treeitems.get_by_names(db=db, name_translations=objective_data["name_translations"], parent_id=db_phase.id):
                print(
                    f"{bcolors.WARNING}Updating existing objective {objective_in_db.name}{bcolors.ENDC}")
                db_objective = await crud.treeitems.update(db=db, db_obj=objective_in_db, obj_in=schemas.TreeItemPatch(**objective_data))
            else:
                objective_name = objective_data.get(
                    "name_translations", {}).get("en", "undefined")
                print(f"{bcolors.OKGREEN}Creating {phase_name} - {objective_name}{bcolors.ENDC}")
                db_objective = await crud.treeitems.create(
                    db=db,
                    obj_in=schemas.TreeItemCreate(
                        **objective_data,
                        parent_id=db_phase.id,
                        type=models.TreeItemTypes.objective
                    )
                )
            touched_objectives.append(db_objective)
            items_resume[objective_data["id"]] = {
                "db_id": db_objective.id,
                "prerequisites": objective_data.get("prerequisites", [])
            }

            task_data: dict
            touched_tasks = []
            for task_data in objective_data["tasks"]:
                if task_in_db := await crud.treeitems.get_by_names(db=db, name_translations=task_data["name_translations"], parent_id=db_objective.id):
                    print(
                        f"{bcolors.WARNING}Updating existing task {task_in_db.name}{bcolors.ENDC}")
                    print(task_in_db.id)
                    db_task = await crud.treeitems.update(db=db, db_obj=task_in_db, obj_in=schemas.TreeItemPatch(**task_data))
                else:
                    task_name = task_data.get(
                        "name_translations", {}).get("en", "undefined")
                    print(
                        f"{bcolors.OKGREEN}Creating {phase_name} - {objective_name} - {task_name}{bcolors.ENDC}")
                    db_task = await crud.treeitems.create(
                        db=db,
                        obj_in=schemas.TreeItemCreate(
                            **task_data,
                            parent_id=db_objective.id,
                            type=models.TreeItemTypes.task,
                        )
                    )
                touched_tasks.append(db_task)

                sum = list(task_data["problemprofiles"]) + \
                    list(objective_data["problemprofiles"])
                await crud.treeitems.sync_problemprofiles(db=db, treeitem=db_task, problemprofiles=sum, commit=False)
               
                items_resume[task_data["id"]] = {
                    "db_id": db_task.id,
                    "prerequisites": task_data.get("prerequisites", [])
                }

            for child in db_objective.children:
                if child not in touched_tasks:
                    print(f"{bcolors.FAIL}Removing task {child.name}{bcolors.ENDC}")
                    await crud.treeitems.remove(db=db, id=child.id)

        for child in db_phase.children:
            if child not in touched_objectives:
                print(f"{bcolors.FAIL}Removing objective {child.name}{bcolors.ENDC}")
                await crud.treeitems.remove(db=db, id=child.id)

    print(items_resume.items())
    for key, resume in items_resume.items():
        db_treeitem = await crud.treeitems.get(db=db, id=resume["db_id"])
        await crud.treeitems.clear_prerequisites(db=db, treeitem=db_treeitem, commit=False)
        for prerequisite_id in resume["prerequisites"]:
            if (ref := prerequisite_id.get("item", None)):
                db_prerequisite = await crud.treeitems.get(
                    db=db, id=items_resume[ref]["db_id"])
                await crud.treeitems.add_prerequisite(db=db, treeitem=db_treeitem, prerequisite=db_prerequisite)

    for child in SCHEMA.children:
        if child not in touched_phases:
            print(f"{bcolors.FAIL}Removing phase {child.name}{bcolors.ENDC}")
            await crud.treeitems.remove(db=db, id=child.id)


async def init():
    db = SessionLocal()
    set_logging_disabled(True)

    try:
        # create problem profiles
        with open("/app/seed/problemprofiles/problemprofiles.json") as json_file:
            for problem in json.load(json_file):
                await create_problemprofile(db, problem)

        # create coproduction schemas
        with open("/app/seed/schemas_DO_NOT_MODIFY.json") as json_file:
            schemas = json.load(json_file)
            for schema_data in schemas:
                await create_coproductionschema(db, schema_data)

        # create external interlinkers first
        for metadata_path in Path("/app/seed/interlinkers").glob("externalsoftware/**/metadata.json"):
            await create_interlinker(db, metadata_path, externalsoftware=True)

        for metadata_path in Path("/app/seed/interlinkers").glob("externalknowledge/**/metadata.json"):
            await create_interlinker(db, metadata_path, externalknowledge=True)

        # create software interlinkers first
        for metadata_path in Path("/app/seed/interlinkers").glob("software/**/metadata.json"):
            await create_interlinker(db, metadata_path, software=True)

        # then knowledge interlinkers
        for metadata_path in Path("/app/seed/interlinkers").glob("knowledge/**/metadata.json"):
            await create_interlinker(db, metadata_path, knowledge=True)

    except Exception as e:
        raise e

    db.close()

if __name__ == "__main__":
    logger.info("Creating initial data")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
    logger.info("Initial data created")
