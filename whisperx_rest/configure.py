"""Swagger configuration script generates static/swagger.json"""

import os
import ast
import inspect
import json
from whisperx import transcribe  # pylint: disable=import-error; type: ignore


def find_args(
    source_code: str, func_value: str, func_attr: str
):  # -> Generator[dict[str, Any], Any, None]
    """Finds arguments passed to parser.add_argument() calls in module source code

    Args:
        source_code (str): module source code
        func_value (str): object name
        func_attr (str): method name

    Yields:
        Generator[dict[str, str | None]]: dict of args and kwargs of every method call
    """
    tree = ast.parse(source_code)

    for i in ast.walk(tree):
        if (
            isinstance(i, ast.Call)
            and isinstance(i.func, ast.Attribute)
            and i.func.attr == func_attr
            and ast.unparse(i.func.value) == func_value
        ):
            yield {
                "args": [ast.unparse(j) for j in i.args],
                "kwargs": {j.arg: ast.unparse(j.value) for j in i.keywords},
            }


def main():
    """main function"""
    # Get source code of the whisperx cli module
    module_source = inspect.getsource(transcribe)
    static_dir = os.path.dirname(__file__) + "/static"

    parameters = []
    # Parse module source code to find whisperx cli arguments
    for argument in find_args(module_source, "parser", "add_argument"):
        arg_name = argument["args"][0].strip("'").replace("--", "")
        # Skip parameters that mustn't be changed
        if arg_name in ["device", "model_dir", "output_dir"]:
            continue
        # Pass default value if set
        default_value = (
            argument["kwargs"]["default"].strip("'")
            if "default" in argument["kwargs"].keys()
            else ""
        )
        # Create dict and append it to the list of API parameters
        parameters += [
            {
                "in": "formData" if arg_name == "audio" else "query",
                "name": arg_name,
                "description": argument["kwargs"]["help"].strip("'"),
                "required": False,
                "type": "file" if arg_name == "audio" else "string",
                "default": default_value.replace("None", ""),
            }
        ]

    # Read swagger json config file template
    with open(f"{static_dir}/swagger_template.json", "r", encoding="utf8") as f:
        swagger_json = json.loads(f.read())

    # Put arguments to template
    swagger_json["paths"]["/whisperx"]["post"]["parameters"] += parameters

    # Save swagger json config
    with open(f"{static_dir}/swagger.json", "w", encoding="utf8") as f:
        f.write(json.dumps(swagger_json))


if __name__ == "__main__":
    main()
