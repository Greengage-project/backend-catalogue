from pathlib import Path
import json, os

# Expected structure for metadata.json
EXPECTED_STRUCTURE_METADATA = {
    "author": {"required": True, "type": str},
    "description_translations": {"required": True, "type": dict},
    "environments": {"required": True, "type": list},
    "id": {"required": True, "type": str},
    "languages": {"required": True, "type": list},
    "licence": {"required": True, "type": str},
    "name_translations": {"required": True, "type": dict},
    "tags_translations": {"required": True, "type": dict},
}

# Expected structure for the phase JSON files
EXPECTED_STRUCTURE_PHASE = {
    "id": {"required": True, "type": str},
    "prerequisites": {"required": True, "type": list},
    "name_translations": {"required": True, "type": dict},
    "description_translations": {"required": True, "type": dict},
    "objectives": {
        "required": True,
        "type": list,
        "structure": {
            "name_translations": {"required": True, "type": dict},
            "description_translations": {"required": True, "type": dict},
            "problemprofiles": {"required": False, "type": list},
            "tasks": {
                "required": True,
                "type": list,
                "structure": {
                    "name_translations": {"required": True, "type": dict},
                    "description_translations": {"required": True, "type": dict},
                    "problemprofiles": {"required": False, "type": list},
                    "id": {"required": True, "type": str},
                    "prerequisites": {"required": False, "type": list},
                },
            },
            "id": {"required": True, "type": str},
            "prerequisites": {"required": False, "type": list},
        },
    },
}

# Icons for messages
CHECK_MARK = "\u2705"  # ✓
CROSS_MARK = "\u274C"  # ✗


def validate_structure(data, structure, path="root"):
    """Validate the structure of JSON data against the expected structure."""
    errors = []
    for key, rules in structure.items():
        full_path = f"{path}.{key}"
        if key not in data:
            if rules.get("required", False):
                errors.append(f"{CROSS_MARK} Missing required attribute '{full_path}'")
        else:
            # Check type
            if not isinstance(data[key], rules["type"]):
                errors.append(
                    f"{CROSS_MARK} '{full_path}' should be of type '{rules['type'].__name__}', "
                    f"but got '{type(data[key]).__name__}'"
                )
            # Recursive check for nested structures
            if "structure" in rules and isinstance(data[key], (dict, list)):
                if isinstance(data[key], list):
                    for i, item in enumerate(data[key]):
                        errors.extend(
                            validate_structure(
                                item, rules["structure"], path=f"{full_path}[{i}]"
                            )
                        )
                elif isinstance(data[key], dict):
                    errors.extend(
                        validate_structure(
                            data[key], rules["structure"], path=full_path
                        )
                    )
    return errors


def check_json_file(file_path, structure, file_name):
    """Load a JSON file and validate its structure."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            errors = validate_structure(data, structure, path=file_name)
            if errors:
                print(f"{CROSS_MARK} Errors in '{file_name}':")
                for error in errors:
                    print(f"  - {error}")
            else:
                print(
                    f"{CHECK_MARK} '{file_name}' is valid and contains all required attributes."
                )
    except json.JSONDecodeError:
        print(f"{CROSS_MARK} JSON error in '{file_name}': the file is not well-formed.")


def check_metadata_in_folders(root_directory):
    """Check each folder in the root directory for a metadata.json file and validate it."""
    for folder_path in Path(root_directory).iterdir():
        if folder_path.is_dir():
            print(f"\n=== Checking folder: '{folder_path.name}' ===")

            # Validate metadata.json
            metadata_path = folder_path / "metadata.json"
            if metadata_path.is_file():
                print(f"\nValidating '{folder_path.name}/metadata.json'")
                check_json_file(
                    metadata_path,
                    EXPECTED_STRUCTURE_METADATA,
                    f"{folder_path.name}/metadata.json",
                )
            else:
                print(f"{CROSS_MARK} No metadata.json found in '{folder_path.name}'.")

            # Validate phase JSON files in the phases subfolder
            phases_path = folder_path / "phases"
            if phases_path.is_dir():
                for phase_file in phases_path.glob("*.json"):
                    print(f"Validating '{folder_path.name}/phases/{phase_file.name}'")
                    check_json_file(
                        phase_file,
                        EXPECTED_STRUCTURE_PHASE,
                        f"{folder_path.name}/phases/{phase_file.name}",
                    )
            else:
                print(
                    f"{CROSS_MARK} No phases directory found in '{folder_path.name}'."
                )


root_directory = os.getcwd()
check_metadata_in_folders(root_directory)
