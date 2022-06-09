""""
The file contains utilities useful for generating a new
step code. 

This is useful as there is lots of boilerplate that needs
to be written, and if we can cut it down to zero, that is
ideal!

To run this file, simply run python dev/create_new_steps.py
and follow the prompts.
"""

import os
from pathlib import Path
from typing import Dict, Tuple

# Constants useful in f strings, since they can't contain brackets
OPEN_BRACKET = "{"
CLOSE_BRACKET = "}"

# Markers in the code that this script uses to find where to insert code
IMPORT_MARKER = "# AUTOGENERATED LINE: IMPORT (DO NOT DELETE)"
EXPORT_MARKER = "# AUTOGENERATED LINE: EXPORT (DO NOT DELETE)"
TEST_MARKER = "# AUTOGENERATED LINE: TEST (DO NOT DELETE)"
STEPTYPE_MARKER = "// AUTOGENERATED LINE: STEPTYPE (DO NOT DELETE)"
API_MARKER = "// AUTOGENERATED LINE: API (DO NOT DELETE)"

# Types that step parameters can use in a valid way
VALID_PARAMETER_TYPES = [
    'int', 'float', 'str', 'bool',
    'ColumnID', 'List[ColumnID]', 
    'Any'
]

def get_step_performers_folder() -> Path:
    return Path('./mitosheet/step_performers')

def get_code_chunk_folder() -> Path:
    return Path('./mitosheet/code_chunks')

def get_test_folder() -> Path:
    return Path('./mitosheet/tests/step_performers')

def get_step_name(original_step_name: str) -> str:
    return original_step_name.lower().replace(' ', '_')

def get_step_performer_name_and_import_statement(original_step_name: str) -> Tuple[str, str]:
    step_name = get_step_name(original_step_name)
    step_performer_name = original_step_name.replace(' ', '') + "StepPerformer"
    return (
        step_performer_name,
        f'from mitosheet.step_performers.{step_name} import {step_performer_name}'
    )

def get_code_chunk_name_and_import_statement(original_step_name: str) -> Tuple[str, str]:
    step_name = get_step_name(original_step_name)
    code_chunk_name = original_step_name.replace(' ', '') + "CodeChunk"
    return (
        code_chunk_name,
        f'from mitosheet.code_chunks.{step_name}_code_chunk import {code_chunk_name}'
    )

def get_params_getter_code(params: Dict[str, str], on_self: bool=False) -> str:
    params_code = ""

    for param_name, param_type in params.items():
        if not on_self:
            params_code += f'{param_name}: {param_type} = get_param(params, \'{param_name}\')\n        '
        else:
            params_code += f'{param_name}: {param_type} = self.get_param(\'{param_name}\')\n        '

    return params_code

def get_step_performer_code(original_step_name: str, params: Dict[str, str]) -> str:
    step_name = get_step_name(original_step_name)
    (step_performer_name, _) = get_step_performer_name_and_import_statement(original_step_name) 
    (code_chunk_name, code_chunk_import_path) = get_code_chunk_name_and_import_statement(original_step_name) 
    params_code = get_params_getter_code(params)

    return f"""
#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.

from time import perf_counter
from typing import Any, Dict, List, Optional, Set, Tuple
from mitosheet.code_chunks.code_chunk import CodeChunk
{code_chunk_import_path}

from mitosheet.state import State
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.step_performers.utils import get_param
from mitosheet.types import ColumnID

class {step_performer_name}(StepPerformer):
    \"\"\"
    Allows you to {step_name.replace('_', ' ')}.
    \"\"\"

    @classmethod
    def step_version(cls) -> int:
        return 1

    @classmethod
    def step_type(cls) -> str:
        return '{step_name}'

    @classmethod
    def execute(cls, prev_state: State, params: Dict[str, Any]) -> Tuple[State, Optional[Dict[str, Any]]]:
        {params_code}

        # We make a new state to modify it
        post_state = prev_state.copy() # TODO: update the deep copies

        pandas_start_time = perf_counter()
        
        # TODO: do the operation here

        pandas_processing_time = perf_counter() - pandas_start_time


        return post_state, {OPEN_BRACKET}
            'pandas_processing_time': pandas_processing_time,
            'result': {OPEN_BRACKET}
                # TODO: fill in the result
            {CLOSE_BRACKET}
        {CLOSE_BRACKET}

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        params: Dict[str, Any],
        execution_data: Optional[Dict[str, Any]],
    ) -> List[CodeChunk]:
        return [
            {code_chunk_name}(prev_state, post_state, params, execution_data)
        ]

    @classmethod
    def get_modified_dataframe_indexes(cls, params: Dict[str, Any]) -> Set[int]:
        return {OPEN_BRACKET}get_param(params, 'sheet_index'){CLOSE_BRACKET} # TODO: add the modified indexes here!
    """

def get_code_chunk_code(original_step_name: str, params: Dict[str, str]) -> str:
    (code_chunk_name, _) = get_code_chunk_name_and_import_statement(original_step_name) 
    params_code = get_params_getter_code(params, on_self=True)

    return f"""
#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.
from typing import List
from mitosheet.code_chunks.code_chunk import CodeChunk
from mitosheet.types import ColumnID

class {code_chunk_name}(CodeChunk):

    def get_display_name(self) -> str:
        return '{original_step_name}'
    
    def get_description_comment(self) -> str:
        {params_code}
        return "TODO"

    def get_code(self) -> List[str]:
        {params_code}

        # TODO: actually generate the code here!

        return []

    
    def get_edited_sheet_indexes(self) -> List[int]:
        return [] # TODO: return this here!
    """

# This function actually writes the given code to the given file
def write_python_code_file(path_to_file: Path, code: str) -> None:
    if os.path.exists(path_to_file):
        clear = input(f'{path_to_file} already exists, do you want to clear it?: [y/n]').lower().startswith('y')
        if clear:
            os.remove(path_to_file)
        else:
            print("Ok... exiting")
            exit(1)
    
    with open(path_to_file, 'w+') as f:
        f.write(code)

def write_step_performer(original_step_name: str, params: Dict[str, str]) -> None:
    step_name = get_step_name(original_step_name)
    path_to_file = get_step_performers_folder() / (step_name + '.py') 
    step_performer_code = get_step_performer_code(original_step_name, params)
    write_python_code_file(path_to_file, step_performer_code)

def write_code_chunk(original_step_name: str, params: Dict[str, str]) -> None:
    step_name = get_step_name(original_step_name)
    path_to_file = get_code_chunk_folder() / (step_name + '_code_chunk.py') 
    step_performer_code = get_code_chunk_code(original_step_name, params)
    write_python_code_file(path_to_file, step_performer_code)

def write_to_step_performer_init(original_step_name: str) -> None:
    path_to_init = get_step_performers_folder() / '__init__.py'
    (step_performer_name, step_performer_import_statement) = get_step_performer_name_and_import_statement(original_step_name) 

    with open(path_to_init, 'r') as f:
        code = f.read()
        code = code.replace(IMPORT_MARKER, f"{step_performer_import_statement}\n{IMPORT_MARKER}")
        code = code.replace(EXPORT_MARKER, f"{step_performer_name},\n    {EXPORT_MARKER}")

    with open(path_to_init, 'w') as f:
        f.write(code)

def get_params_parameter_code(params: Dict[str, str]) -> str:
    params_parameter_code = ""
    for param_name, param_type in params.items():
        # If we are working with column_ids, we turn them into headers
        param_name = param_name.replace('_id', '_header')
        param_type = param_type.replace("ColumnID", "ColumnHeader")

        # NOTE: we turn column ids to column headers in the calling function for the test file
        params_parameter_code += f'{param_name}: {param_type},\n            '
    
    return params_parameter_code.strip()

def get_id_to_header_code(params: Dict[str, str]) -> str:
    id_to_header_code = ""
    for param_name, param_type in params.items():
        if param_type == 'ColumnID':
            id_to_header_code += f"""{param_name} =self.mito_widget.steps_manager.curr_step.column_ids.get_column_id_by_header(
            sheet_index,
            {param_name.replace('_id', '_header')}
        )\n"""
        if param_type == 'List[ColumnID]':
            id_to_header_code += f"""{param_name} = [
            self.mito_widget.steps_manager.curr_step.column_ids.get_column_id_by_header(sheet_index, column_header)
            for column_header in {param_name.replace('_id', '_header')}
        ]"""
    return id_to_header_code

def get_test_util_function_code(original_step_name: str, params: Dict[str, str]) -> str:
    
    step_name = get_step_name(original_step_name)
    params_parameter_code = get_params_parameter_code(params)
    id_to_header_code = get_id_to_header_code(params)

    params_pass_code = ""
    for param in params:
        params_pass_code += f'\'{param}\': {param},\n                    '
    params_pass_code.strip()

    return f"""
    @check_transpiled_code_after_call
    def {step_name}(
            self, 
            {params_parameter_code}
        ) -> bool:

        {id_to_header_code}

        return self.mito_widget.receive_message(
            self.mito_widget,
            {OPEN_BRACKET}
                'event': 'edit_event',
                'id': get_new_id(),
                'type': '{step_name}_edit',
                'step_id': get_new_id(),
                'params': {OPEN_BRACKET}
                    {params_pass_code}
                {CLOSE_BRACKET}
            {CLOSE_BRACKET}
        )
    """

def write_to_test_utility(original_step_name: str, params: Dict[str, str]) -> None:
    path_to_test_util = './mitosheet/tests/test_utils.py'

    with open(path_to_test_util, 'r') as f:
        code = f.read()
        code = code.replace(TEST_MARKER, f"{get_test_util_function_code(original_step_name, params)}\n{TEST_MARKER}")

    with open(path_to_test_util, 'w') as f:
        f.write(code)


def read_params() -> Dict[str, str]:
    param_names = input("Enter a comma seperated list of param nams: [sheet_index, column_ids, ...] ").replace(' ', '').split(',')
    
    params = {}
    for param_name in param_names:
        type = ''
        while type not in VALID_PARAMETER_TYPES:
            type = input(f'Select a type from {VALID_PARAMETER_TYPES} for {param_name}: ')
        params[param_name] = type
    
    return params

def get_test_file_code(original_step_name: str, params: Dict[str, str]) -> str:
    step_name = get_step_name(original_step_name)
    params_string = ", ".join(params.keys())

    return f"""#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.
\"\"\"
Contains tests for {original_step_name}
\"\"\"

import pandas as pd
import pytest
from mitosheet.tests.test_utils import create_mito_wrapper_dfs

{step_name.upper()}_TESTS = [
    (
        [
            pd.DataFrame({OPEN_BRACKET}'A': [1, 2, 3], 'B': [1.0, 2.0, 3.0], 'C': [True, False, True], 'D': ["string", "with spaces", "and/!other@characters"], 'E': pd.to_datetime(['12-22-1997', '12-23-1997', '12-24-1997']), 'F': pd.to_timedelta(['1 days', '2 days', '3 days']){CLOSE_BRACKET})
        ],
        "put", 
        "params", 
        "here",
        [
            pd.DataFrame({OPEN_BRACKET}'A': [1, 2, 3], 'B': [1.0, 2.0, 3.0], 'C': [True, False, True], 'D': ["string", "with spaces", "and/!other@characters"], 'E': pd.to_datetime(['12-22-1997', '12-23-1997', '12-24-1997']), 'F': pd.to_timedelta(['1 days', '2 days', '3 days']){CLOSE_BRACKET})
        ]
    ),
]
@pytest.mark.parametrize(\"input_dfs, {params_string}, output_dfs\", {step_name.upper()}_TESTS)
def test_{step_name}(input_dfs, {params_string}, output_dfs):
    mito = create_mito_wrapper_dfs(*input_dfs)

    mito.{step_name}({params_string})

    assert len(mito.dfs) == len(output_dfs)
    for actual, expected in zip(mito.dfs, output_dfs):
        assert actual.equals(expected)"""

def write_testing_file(original_step_name: str, params: Dict[str, str]) -> None:
    step_name = get_step_name(original_step_name)
    path_to_file = get_test_folder() / ("test_" + step_name + '.py') 
    test_file_code = get_test_file_code(original_step_name, params)
    write_python_code_file(path_to_file, test_file_code)


def get_src_folder() -> Path:
    return Path('src/')
    
def write_to_types_file(original_step_name: str) -> None:
    path_to_types = get_src_folder() / 'types.tsx'

    step_name = get_step_name(original_step_name)
    enum_name = original_step_name.title().replace(' ', '')

    with open(path_to_types, 'r') as f:
        code = f.read()
        code = code.replace(STEPTYPE_MARKER, f"{enum_name} = '{step_name}',\n")

    with open(path_to_types, 'w') as f:
        f.write(code)

def get_typescript_type_for_param(param_name: str, param_type: str) -> str:
    if param_type == 'int' or param_type == 'float':
        return 'number'
    elif param_type == 'str':
        return 'string'
    elif param_type == 'bool':
        return 'boolean'
    elif param_type == 'ColumnID':
        return 'ColumnID'
    elif param_type == 'List[ColumnID]':
        return 'ColumnID[]'
    elif param_type == 'Any':
        return input(f'What is the Typescript type for {param_name}')
    else:
        raise Exception(f'{param_name} of type {param_type} is an unsupported type')

def get_api_function_params(params: Dict[str, str]) -> str:

    final_params = ''

    for param_name, param_type in params.items():
        final_params += f'        {param_name}: {get_typescript_type_for_param(param_name, param_type)},\n'
    
    return final_params.strip()


def get_api_function_params_for_send(params: Dict[str, str]) -> str:
    final_params = ''

    for param_name in params.keys():
        final_params += f'                {param_name}: {param_name},\n'
    
    return final_params.strip()
    

def get_api_function_code(original_step_name: str, params: Dict[str, str]) -> str:
    step_name = get_step_name(original_step_name)
    enum_name = original_step_name.title().replace(' ', '')

    return f"""
    async edit{enum_name}(
        {get_api_function_params(params)}
    ): Promise<void> {OPEN_BRACKET}

        const stepID = getRandomId();
        await this.send({OPEN_BRACKET}
            'event': 'edit_event',
            'type': '{step_name}_edit',
            'step_id': stepID,
            'params': {OPEN_BRACKET}
                {get_api_function_params_for_send(params)}
            {CLOSE_BRACKET}
        {CLOSE_BRACKET}, {OPEN_BRACKET}{CLOSE_BRACKET})
    {CLOSE_BRACKET}
    
    """

def write_to_api_file(original_step_name: str, params: Dict[str, str]) -> None:
    path_to_api = get_src_folder() / 'jupyter' / 'api.tsx'

    with open(path_to_api, 'r') as f:
        code = f.read()
        code = code.replace(API_MARKER, get_api_function_code(original_step_name, params))

    with open(path_to_api, 'w') as f:
        f.write(code)

def main() -> None:
    """
    This bit of meta-programming makes it easy to quickly generate the barebones
    of a new step type, adding files in the right locations, etc. In the future,
    we can build onto to this to make it much quicker to add new steps, which
    will be a nice thing for us.
    """
    print("Welcome to the Mito step generator. This will walk you through the process of generating a new step...")
    original_step_name = input("Step Name: [Fill NaN, Drop Duplicates] ")
    params = read_params()

    # First, we change all the Python files
    write_step_performer(original_step_name, params)
    print("Wrote step performer")
    write_code_chunk(original_step_name, params)
    print("Wrote code chunk")
    write_to_step_performer_init(original_step_name)
    print("Wrote to init")
    write_to_test_utility(original_step_name, params)
    print("Wrote to test utilities")
    write_testing_file(original_step_name, params)
    print("Wrote testing file")

    # Then, we change the frontend files
    write_to_types_file(original_step_name)
    print("Wrote to Types.tsx")
    write_to_api_file(original_step_name, params)
    print("Wrote to api.tsx")


    # TODO:
    # 1. Add a new step type in Types.tsx
    # 2. Auto generate the api files
    # 3. Be able to specify that we're creating a taskpane and then take the step parameters passed in a particular order and create a UI for them. For example, if sheet_index is the first param provided, then it should create a taskpane with a Dataframe -> DfName seletc.
    # 4. Be able to read the params back in correctly (and do some refactoring!)
    # 5. Be able to do upgrade refactoring automatically - just tell it how to migrate



if __name__ == "__main__":
    main()
