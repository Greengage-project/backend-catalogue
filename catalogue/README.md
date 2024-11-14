# Interlinkers data

**Current version status:**

[![Testing](https://github.com/interlink-project/interlinkers-data/actions/workflows/run-test.yml/badge.svg)](https://github.com/interlink-project/interlinkers-data/actions/workflows/run-test.yml)

In here we will indicate the steps to follow to create a BUNDLE for a KNOWLEDGE or SOFTWARE INTERLINKER that can be imported directly by the INTERLINKER catalogue

The schemas implemented are based on what have been discussed here: 

https://docs.google.com/spreadsheets/d/1tJ2BfX4EOdbBqEbrJWg8a3MENw13vYiPZM_S4wWWgWQ/edit


# For users
The way to add new interlinkers is to create a new directory that follows the structure defined by the example.
 
* A "metadata.json" file in the root of the directory.
* Optionally, a directory called "snapshots" can be created to store the images corresponding to the interlinker. The order is important; use digits to order them (image1, image2, image3...)
    * Allowed formats: '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif'

```
.
├── base.py
├── knowledge
│   ├── example_knowledge_interlinker
│   │   ├── doc.docx
│   │   ├── instructions.md
│   │   ├── metadata.json
│   │   └── snapshots
│   │       ├── image1.jpeg
│   │       └── image2.jpeg
│
│   ...
│
│   ├── schema.json
│   └── schema.py
├── software
│   ├── ceditor
│   │   ├── logo.jpeg
│   │   ├── metadata.json
│   │   └── snapshots
│   │       └── screenshot.png
│   ├── googledrive
│   │   ├── logo.png
│   │   ├── metadata.json
│   │   └── snapshots
│   │       ├── docs.png
│   │       ├── sheets.png
│   │       └── slides.png
│
│   ...
│
│   ├── schema.json
│   └── schema.py
└── test.py
```

## Adding new knowledge interlinker

In the case of adding a new KNOWLEDGE INTERLINKER, the following sections must be included in the metadata.json:

```yaml
{
    OUTDATED
    
}
```

For example:
```json
{
    OUTDATED
}
```

For **representations**, for now, only these software interlinkers are available:

* **Google Drive** (googledrive):
    * **file:** path to a file, such as .docx, .ppt, .xlsx, .pdf... anything that google drive could work with.
    * **softwareinterlinker:** "googledrive"

* **Survey** (survey):

    * **file:** go to https://surveyjs.io/create-survey-v2, create a survey and copy the data that appears in the "JSON Editor" tab. Then, create a file with ".json" extension and copy the contents copied. File attribute should point to the path of this file you just created.

        ![survey creation](images/survey.gif)

    * **softwareinterlinker:** "survey"

* **Collaborative editor** (ceditor):

    * **file:** you have several options:
    
        * Go to https://yopad.eu, create a pad (you can import docx files) and download the data as Etherpad / HTML / Microsoft Word or ODF. Then, move that file to the folder and set the path of the file attribute.

            ![pad creation](images/pad.gif)

    * **softwareinterlinker**: "ceditor"

        
## How to validate data

Enter
https://www.jsonschemavalidator.net/


If you want to check metadata for a KNOWLEDGE interlinker, open [/knowledge/schema.json](/knowledge/schema.json) file and copy its content into the left part. Now, copy the metadata.json into the right part.

![correct](images/correct.png)

Incorrect metadata.json (tags length < 1)

![incorrect](images/incorrect.png)

> :warning: **Paths of files are not validated with this method**: Be very careful here!

# For developers


## Testing

To test that all the metadata files are valid, a script called "test.py" is provided, which in addition to validating the metadata, creates a file "schema.json" at the height of "schema.py" that users can use to quickly validate if the metadata is correct, without having to use python at all, as can be seen in "For users" section.

#### Install the dependencies:
```sh
pip3 install pydantic
```

#### Run the script:
```sh
python3 test.py
```

![test](images/test.gif)


### Github action to test on versions push

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: checkout repo content
        uses: actions/checkout@v2 # checkout the repository content to github runner.
      - name: setup python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8 #install the python needed
      - name: Install dependencies and run test script
        run: |
          python -m pip install --upgrade pip
          pip3 install pydantic
          python test.py
```


## What is pydantic and why should you use it?

[Pydantic](https://pydantic-docs.helpmanual.io/) is a useful library for data parsing and validation. It coerces input types to the declared type (using type hints), accumulates all the errors using ValidationError & it’s also well documented making it easily discoverable.

Working with jsonschema can be very tedious and makes schemas difficult to understand, to modify and maintain. Pydantic makes this process easy and can generate jsonschemas.

### Basic examples
```yaml
Free text:               str
Whole number:            int
Decimal:                 float
Boolean:                 bool
Optional text:           Optional[str]
List of texts:           List[str]
Optional array of texts: Optional[List[str]]
```

```py
class Schema(BaseModel):
    name: str
    description: Optional[str]
    tags: List[str]
```

### Enumerations

```py
class Difficulties(Enum):
    very_easy = "very_easy"
    easy = "easy"
    medium = "medium"
    difficult = "difficult"
    very_difficult = "very_difficult"

class Schema(BaseModel):
    difficulty: Difficulties
```

Now difficulty can only be one of the values specified in the enum

### Conditionals:

conbytes, condecimal, confloat, conint, conlist, conset, constr

```py
class Schema(BaseModel):
    tags: conlist(str, min_items=1)
```

### Custom validators

Override a validator for a given attribute. For example, you can validate that the path contained in the file attribute is actually a file:

```py
class Schema(BaseModel):
    value: str

    @validator("value")
    def example_value_validator(cls, v):
        if not value in ["example", "value"]:
            raise ValueError(
                f"{file} does not exist. Example: example_knowledge_interlinker/resources/doc.docx"
            )
        return v

```

### Nested objects

```py
class File(BaseModel):
    name: str
    path: str
    thumbnail: Optional[str]

class Schema(BaseModel):
    name: str
    file: File
    
```

```json
{
    "name": "example",
    "file": {
        "name": "filename",
        "path": "/home/doc.docx",
        "thumbnail": "/home/logo.png"
    }
}
```

### How to validate data
```py
data = {
    "name": "...",
    "description": "...",
    "tags": [ ... ],
    ...
}

Schema(**data)
# if not valid, raises exception
```


### Extra attributes forbidden 

If the schema is instantiated with more attributes than specified in it, it fails

```py
from pydantic import BaseModel, Extra

data = {
    "name": "example",
    "description": "description",
    "image": "image"
}
class InterlinkerSchema(BaseModel, extra=Extra.forbid):
    name: str
    description: str

InterlinkerSchema(**data)

```
Raises:
```
pydantic.error_wrappers.ValidationError: 1 validation error for InterlinkerSchema
image
  extra fields not permitted (type=value_error.extra)
```

> Take a look at pydantic documentation for more field types: https://pydantic-docs.helpmanual.io/usage/types/


## Interlinker schemas

### Base interlinker schema

This scheme defines the common properties for SOFTWARE and KNOWLEDGE INTERLINKERs. It is located in the root of the repository with the name of "base.py".

./base.py

Defines these attributes:

* name
* description
* tags
* difficulty
* targets
* problemprofiles
* types
* administrative_scope
* domain
* process
* constraints_and_limitations_translations
* regulations_and_standards_translations
* overview_text

(Some of them are not required for the first phase, so are marked as optional)

### KNOWLEDGE INTERLINKER schema

/knowledge/schema.py

Extends the base with these attributes:

* instructions
* representations
    * file
    * form
    * format
    * softwareinterlinker

### SOFTWARE INTERLINKER schema

/software/schema.py

Extends the base with these attributes:
* supported_by
* auth_method
* deployment_manual
* user_manual
* developer_manual
* supports_internationalization
* is_responsive
* open_in_modal
* assets_clonable
* path
* is_subdomain



### How to Create a Schema - Step-by-Step Guide

1. **Duplicate an Existing Schema**  
   Go to `backend-catalogue/catalogue/seed/schemas` and copy one of the existing schemas, such as the "default" schema.

2. **Edit Schema Files**  
   Modify the `metadata.json` file and the JSON files in the `phases` folder, adapting them to fit your requirements.

3. **Run Schema Validation**  
   In the same folder, run the schema validation script located at `backend-catalogue/catalogue/seed/schemas/validate_schemas.py`.

4. **Generate the Schema**  
   Still in the same folder, run `backend-catalogue/catalogue/seed/generate.py` to add your new schema to the existing ones.

5. **Build and Integrate the Schema**  
   - **If on a local environment**:  
     Navigate to the `backend-catalogue` folder and run `make build`, followed by `make integrated`.
   - **If on production**:  
     Download the latest version of the container image.

6. **Deploy the Schema in Production**  
   Access the container where the image is deployed and run `bash seed.sh`.