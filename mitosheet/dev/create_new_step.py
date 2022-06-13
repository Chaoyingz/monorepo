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
import shutil
from typing import Dict, List, Tuple

# Constants useful in f strings, since they can't contain brackets
OPEN_BRACKET = "{"
CLOSE_BRACKET = "}"

# Markers in the code that this script uses to find where to insert code
IMPORT_MARKER = "# AUTOGENERATED LINE: IMPORT (DO NOT DELETE)"
EXPORT_MARKER = "# AUTOGENERATED LINE: EXPORT (DO NOT DELETE)"
TEST_MARKER = "# AUTOGENERATED LINE: TEST (DO NOT DELETE)"
STEPTYPE_MARKER = "// AUTOGENERATED LINE: STEPTYPE (DO NOT DELETE)"
ACTIONENUM_MARKER = "// AUTOGENERATED LINE: ACTIONENUM (DO NOT DELETE)"
ACTION_MARKER = "// AUTOGENERATED LINE: ACTION (DO NOT DELETE)"
API_MARKER = "// AUTOGENERATED LINE: API (DO NOT DELETE)"
TASKPANETYPE_MARKER = "// AUTOGENERATED LINE: TASKPANETYPE (DO NOT DELETE)"
TASKPANEINFO_MARKER = "// AUTOGENERATED LINE: TASKPANEINFO (DO NOT DELETE)"
EDITINGTASKPANE_MARKER = "// AUTOGENERATED LINE: EDITINGTASKPANE (DO NOT DELETE)"
ALLOWUNDOREDOEDITINGTASKPANE_MARKER = "// AUTOGENERATED LINE: ALLOWUNDOREDOEDITINGTASKPANE (DO NOT DELETE)"
MITOIMPORT_MARKER = "// AUTOGENERATED LINE: MITOIMPORT (DO NOT DELETE)"
GETCURROPENTASKPANE_MARKER = "// AUTOGENERATED LINE: GETCURROPENTASKPANE (DO NOT DELETE)"

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


def create_folder(path_to_folder: Path) -> None:
    if os.path.exists(path_to_folder):
        clear = input(f'{path_to_folder} already exists, do you want to clear it?: [y/n]').lower().startswith('y')
        if clear:
            shutil.rmtree(path_to_folder)
        else:
            print("Ok... exiting")
            exit(1)

    os.mkdir(path_to_folder)

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

def add_enum_value(path: Path, marker: str, key: str, value: str) -> None:

    with open(path, 'r') as f:
        code = f.read()
        code = code.replace(marker, f"{key} = '{value}',\n    {marker}")

    with open(path, 'w') as f:
        f.write(code)
    
def write_steptype_to_types_file(original_step_name: str) -> None:
    path_to_types = get_src_folder() / 'types.tsx'

    step_name = get_step_name(original_step_name)
    enum_name = original_step_name.title().replace(' ', '')

    add_enum_value(path_to_types, STEPTYPE_MARKER, enum_name, step_name)

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

def get_default_typescript_value_for_param(param_name: str, param_type: str) -> str:
    if param_name == 'sheet_index':
        return 'sheetIndex'

    if param_type == 'int' or param_type == 'float':
        return '0'
    elif param_type == 'str':
        return 'Random String'
    elif param_type == 'bool':
        return 'true'
    elif param_type == 'ColumnID':
        return 'TODO'
    elif param_type == 'List[ColumnID]':
        return '[]'
    elif param_type == 'Any':
        return input(f'What is the default value for {param_name}')
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
    
    {API_MARKER}
    """

def write_to_api_file(original_step_name: str, params: Dict[str, str]) -> None:
    path_to_api = get_src_folder() / 'jupyter' / 'api.tsx'

    with open(path_to_api, 'r') as f:
        code = f.read()
        code = code.replace(API_MARKER, get_api_function_code(original_step_name, params))

    with open(path_to_api, 'w') as f:
        f.write(code)

def get_action_code(original_step_name: str, enum_name: str, create_taskpane: bool) -> str:

    taskpane_type = original_step_name.upper().replace(' ', '_')
    if create_taskpane:
        action_function_code = f"""// We turn off editing mode, if it is on
                setEditorState(undefined);

                setUIState(prevUIState => {OPEN_BRACKET}
                    return {OPEN_BRACKET}
                        ...prevUIState,
                        currOpenTaskpane: {OPEN_BRACKET}type: TaskpaneType.{taskpane_type}{CLOSE_BRACKET},
                        selectedTabType: 'data'
                    {CLOSE_BRACKET}
                {CLOSE_BRACKET})"""
    else:
        action_function_code = f"""// TODO"""

    return f"""[ActionEnum.{enum_name}]: {OPEN_BRACKET}
            type: ActionEnum.{enum_name},
            shortTitle: '{original_step_name}',
            longTitle: '{original_step_name}',
            actionFunction: () => {OPEN_BRACKET}
                {action_function_code}
            {CLOSE_BRACKET},
            isDisabled: () => {OPEN_BRACKET}return undefined{CLOSE_BRACKET}, // TODO
            searchTerms: ['{original_step_name}'],
            tooltip: "{original_step_name}"
        {CLOSE_BRACKET},
        {ACTION_MARKER}
    """

def write_to_actions_file(original_step_name: str, params: Dict[str, str], create_taskpane: bool) -> None:
    path_to_types = get_src_folder() / 'types.tsx'
    path_to_actions = get_src_folder() / 'utils' / 'actions.tsx'

    step_name = get_step_name(original_step_name)
    enum_name = original_step_name.title().replace(' ', '_')

    # First, write the enum
    add_enum_value(path_to_types, ACTIONENUM_MARKER, enum_name, step_name)

    # Then, add a filler for the action
    with open(path_to_actions, 'r') as f:
        code = f.read()
        code = code.replace(ACTION_MARKER, get_action_code(original_step_name, enum_name, create_taskpane))

    with open(path_to_actions, 'w') as f:
        f.write(code)

def get_params_interface_code(original_step_name: str, params: Dict[str, str]) -> str:
    step_name_capital = original_step_name.replace(' ', '')

    params_interface = f"interface {step_name_capital}Params {OPEN_BRACKET}\n"
    for param_name, param_type in params.items():
        params_interface += f'    {param_name}: {get_typescript_type_for_param(param_name, param_type)},\n'
    params_interface += "}"

    return params_interface

def get_default_params(params: Dict[str, str]) -> str:
    default_params = "{\n"
    for param_name, param_type in params.items():
        default_params += f'        {param_name}: {get_default_typescript_value_for_param(param_name, param_type)},\n'
    default_params += "    }"
    return default_params


def get_effect_code(original_step_name: str, params: Dict[str, str], is_live_updating_taskpane: bool) -> str:
    step_name_capital = original_step_name.replace(' ', '')
   
    if is_live_updating_taskpane:
        return f"""const {OPEN_BRACKET}params, setParams{CLOSE_BRACKET} = useLiveUpdatingParams(
        () => getDefaultParams(props.sheetDataArray, props.selectedSheetIndex),
        StepType.{step_name_capital}, 
        props.mitoAPI,
        props.analysisData,
        50
    )"""
    else:
        return f"""const {OPEN_BRACKET}params, setParams, loading, edit, editApplied{CLOSE_BRACKET} = useSendEditOnClick<{step_name_capital}Params, undefined>(
            () => getDefaultParams(props.sheetDataArray, props.selectedSheetIndex),
            StepType.{step_name_capital}, 
            props.mitoAPI,
            props.analysisData,
        )"""

def get_param_user_input_code(param_name: str, param_type: str, is_live_updating_taskpane: bool) -> Tuple[str, List[str]]:

    # If this is selecting a sheet index, use a sheet index select
    if 'sheet_index' in param_name and param_type == 'int':

        # Row, Col, Select, DropdownItem
        return ("""<Row justify='space-between' align='center' title='Select a dataframe TODO.'>
                    <Col>
                        <p className='text-header-3'>
                            Dataframe
                        </p>
                    </Col>
                    <Col>
                        <Select
                            value={props.sheetDataArray[params.sheet_index]?.dfName}
                            onChange={(newDfName: string) => {
                                const newSheetIndex = props.sheetDataArray.findIndex((sheetData) => {
                                    return sheetData.dfName == newDfName;
                                })
                                
                                setParams(prevParams => {
                                    const newParams = getDefaultParams(props.sheetDataArray, newSheetIndex);
                                    if (newParams) {
                                        return newParams;
                                    }
                                    return {
                                        ...prevParams,
                                        sheet_index: newSheetIndex
                                    }
                                });
                            }}
                            width='medium'
                        >
                            {props.sheetDataArray.map(sheetData => {
                                return (
                                    <DropdownItem
                                        key={sheetData.dfName}
                                        title={sheetData.dfName}
                                    />
                                )
                            })}
                        </Select>
                    </Col>
                </Row>""", ['Row', 'Col', 'Select', 'DropdownItem'])
    if param_type == 'int' or param_type == 'float':
        # TODO: number input
        return '<NumberInput>'
    elif param_type == 'str':
        # TODO: string input
        return (f"""<Row justify='space-between' align='center' title='TODO'>
                        <Col>
                            <p className='text-header-3'>
                                {param_name}
                            </p>
                        </Col>
                        <Col>
                            <Input
                                autoFocus
                                width='medium'
                                value={OPEN_BRACKET}'' + params.fill_method.value{CLOSE_BRACKET}
                                onChange={OPEN_BRACKET}(e) => {OPEN_BRACKET}
                                    const newValue = e.target.value;
                                    
                                    setParams(prevParams => {OPEN_BRACKET}
                                        return {OPEN_BRACKET}
                                            ...prevParams,
                                            {param_name}: newValue
                                        {CLOSE_BRACKET}
                                    {CLOSE_BRACKET})
                                {CLOSE_BRACKET}{CLOSE_BRACKET}
                            />
                        </Col>
                    </Row>""", ['Row', 'Col', 'Input'])
    elif param_type == 'bool':
        # TODO: toggle
        return (f"""<Row justify='space-between' align='center'>
                    <Col>
                            <p className='text-header-3'>
                                {param_name}
                            </p>
                        </Col>
                    <Col>
                        <Toggle 
                            value={OPEN_BRACKET}params.{param_name}{CLOSE_BRACKET}
                            onChange={OPEN_BRACKET}() => {OPEN_BRACKET}
                                setParams(prevConcatParams => {OPEN_BRACKET}
                                    return {OPEN_BRACKET}
                                        ...prevConcatParams,
                                        {param_name}: !prevConcatParams.{param_name}
                                    {CLOSE_BRACKET}
                                {CLOSE_BRACKET})
                            {CLOSE_BRACKET}{CLOSE_BRACKET}                      
                        />
                    </Col>
                </Row>""", ['Row', 'Col', 'Toggle'])
    elif param_type == 'ColumnID':
        # TODO: Do a select here
        return '<Select>'
    elif param_type == 'List[ColumnID]':
        # TODO: multiselect or the other one
        return (f"""<Row justify='space-between' align='center' title='TODO'>
                    <Col>
                        <p className='text-header-3'>
                            {param_name}
                        </p>
                    </Col>
                </Row>
                <MultiToggleBox
                    searchable
                    toggleAllIndexes={OPEN_BRACKET}toggleIndexes{CLOSE_BRACKET}
                    height='medium'
                >
                    {OPEN_BRACKET}Object.entries(sheetData?.columnDtypeMap || {OPEN_BRACKET}{CLOSE_BRACKET}).map(([columnID, columnDtype], index) => {OPEN_BRACKET}
                        const columnIDsMap = sheetData?.columnIDsMap || {OPEN_BRACKET}{CLOSE_BRACKET}
                        const columnHeader = columnIDsMap[columnID];
                        const toggle = params.{param_name}.includes(columnID);

                        return (
                            <MultiToggleItem
                                key={OPEN_BRACKET}index{CLOSE_BRACKET}
                                index={OPEN_BRACKET}index{CLOSE_BRACKET}
                                title={OPEN_BRACKET}getDisplayColumnHeader(columnHeader){CLOSE_BRACKET}
                                rightText={OPEN_BRACKET}getDtypeValue(columnDtype){CLOSE_BRACKET}
                                toggled={OPEN_BRACKET}toggle{CLOSE_BRACKET}
                                onToggle={OPEN_BRACKET}() => {OPEN_BRACKET}
                                    toggleIndexes([index], !toggle)
                                {CLOSE_BRACKET}{CLOSE_BRACKET}
                            />
                        ) 
                    {CLOSE_BRACKET}){CLOSE_BRACKET}
                </MultiToggleBox>""", ['Row', 'Col', 'MultiToggleBox', 'MultiToggleItem'])
    elif param_type == 'Any':
        # TODO: It doesn't do this!
        return f'{OPEN_BRACKET}/* TODO: add the user input for {param_name} of type {param_type} */{CLOSE_BRACKET}'
    else:
        raise Exception(f'{param_name} of type {param_type} is an unsupported type')

def get_taskpane_body_code(params: Dict[str, str], is_live_updating_taskpane: bool) -> Tuple[str, List[str]]:
    # We just do the params in a linear order

    taskpane_body_code = ""
    for param_name, param_type in params.items():
        (body_code, elements) = get_param_user_input_code(param_name, param_type, is_live_updating_taskpane)
        taskpane_body_code += f'{body_code}'
    
    return (taskpane_body_code, elements)

def get_taskpane_imports(is_live_updating_taskpane: bool, used_elements: List[str]) -> str:
    imports = ''
    if is_live_updating_taskpane:
        imports += "import useLiveUpdatingParams from '../../../hooks/useLiveUpdatingParams';"
    else:
        imports += "import useSendEditOnClick from '../../../hooks/useSendEditOnClick';"

    for element in set(used_elements):
        if element == 'Row':
            imports += "import Row from '../../spacing/Row';\n"
        elif element == 'Col':
            imports += "import Col from '../../spacing/Col';\n"
        elif element == 'Select':
            imports += "import Select from '../../elements/Select';\n"
        elif element == 'DropdownItem':
            imports += "import DropdownItem from '../../elements/DropdownItem';\n"
        elif element == 'Input':
            imports += "import Input from '../../elements/Input';\n"
        elif element == 'Toggle':
            imports += "import Toggle from '../../elements/Toggle';\n"
        elif element == 'MultiToggleBox':
            imports += "import MultiToggleBox from '../../elements/MultiToggleBox';\n"
        elif element == 'MultiToggleItem':
            imports += "import MultiToggleItem from '../../elements/MultiToggleItem';\n"
            
        else:
            raise Exception(f'{element} needs to have a import statement defined')
        
    return imports

def get_toggle_all_code(params: Dict[str, str]) -> str:

    # First, find all the multi-toggle box 
    multi_toggle_box_params = filter(lambda x: x[1] == 'List[ColumnID]', params.items())

    if len(multi_toggle_box_params) == 0:
        return ''

    param_name_type = '|'.join(map(lambda x: f'\'{x[0]}\'', multi_toggle_box_params))

    return f"""const toggleIndexes = (param_name: param_name_type, indexes: number[], newToggle: boolean): void => {OPEN_BRACKET}
        const columnIds = Object.keys(props.sheetDataArray[params.sheet_index]?.columnIDsMap) || [];
        const columnIdsToToggle = indexes.map(index => columnIds[index]);

        const newColumnIds = [...params[param_name]];

        columnIdsToToggle.forEach(columnID => {OPEN_BRACKET}
            if (newToggle) {OPEN_BRACKET}
                addIfAbsent(newColumnIds, columnID);
            {CLOSE_BRACKET} else {OPEN_BRACKET}
                removeIfPresent(newColumnIds, columnID);
            {CLOSE_BRACKET}
        {CLOSE_BRACKET})

        setParams(prevParams => {OPEN_BRACKET}
            return {OPEN_BRACKET}
                ...prevParams,
                [param_name]: newColumnIds
            {CLOSE_BRACKET}
        {CLOSE_BRACKET})
    {CLOSE_BRACKET}"""

def get_new_taskpane_code(original_step_name: str, params: Dict[str, str], is_live_updating_taskpane: bool) -> str:

    step_name_capital = original_step_name.replace(' ', '')

    (body_code, used_elements) = get_taskpane_body_code(params, is_live_updating_taskpane)

    return f"""import React from "react";
import MitoAPI from "../../../jupyter/api";
import {OPEN_BRACKET} AnalysisData, SheetData, StepType, UIState, UserProfile {CLOSE_BRACKET} from "../../../types"
{get_taskpane_imports(is_live_updating_taskpane, used_elements)}
import DefaultTaskpane from "../DefaultTaskpane/DefaultTaskpane";
import DefaultTaskpaneBody from "../DefaultTaskpane/DefaultTaskpaneBody";
import DefaultTaskpaneHeader from "../DefaultTaskpane/DefaultTaskpaneHeader";
import DefaultEmptyTaskpane from "../DefaultTaskpane/DefaultEmptyTaskpane";


interface {step_name_capital}TaskpaneProps {OPEN_BRACKET}
    mitoAPI: MitoAPI;
    userProfile: UserProfile;
    setUIState: React.Dispatch<React.SetStateAction<UIState>>;
    analysisData: AnalysisData;
    sheetDataArray: SheetData[];
    selectedSheetIndex: number;
{CLOSE_BRACKET}

{get_params_interface_code(original_step_name, params)}


const getDefaultParams = (
    sheetDataArray: SheetData[], 
    sheetIndex: number,
): {step_name_capital}Params | undefined => {OPEN_BRACKET}

    if (sheetDataArray.length === 0 || sheetDataArray[sheetIndex] === undefined) {OPEN_BRACKET}
        return undefined;
    {CLOSE_BRACKET}

    return {get_default_params(params)}
{CLOSE_BRACKET}


/* 
    This taskpane allows you to {original_step_name.lower()}
*/
const {step_name_capital}Taskpane = (props: {step_name_capital}TaskpaneProps): JSX.Element => {OPEN_BRACKET}

    {get_effect_code(original_step_name, params, is_live_updating_taskpane)}

    if (params === undefined) {OPEN_BRACKET}
        return <DefaultEmptyTaskpane setUIState={OPEN_BRACKET}props.setUIState{CLOSE_BRACKET}/>
    {CLOSE_BRACKET}

    {get_toggle_all_code(params)}

    return (
        <DefaultTaskpane>
            <DefaultTaskpaneHeader 
                header="{original_step_name}"
                setUIState={OPEN_BRACKET}props.setUIState{CLOSE_BRACKET}           
            />
            <DefaultTaskpaneBody>
                {body_code}
            </DefaultTaskpaneBody>
        </DefaultTaskpane>
    )
{CLOSE_BRACKET}

export default {step_name_capital}Taskpane;"""

def write_taskpane_types_file(original_step_name: str, is_editing_taskpane: bool, is_remain_open_undo_redo_taskpane: bool) -> None:
    
    path_to_taskpanes = Path('./src/components/taskpanes/taskpanes.tsx')
    enum_key = original_step_name.upper().replace(' ', '_')
    step_name = get_step_name(original_step_name)

    # First, add to the enum
    add_enum_value(path_to_taskpanes, TASKPANETYPE_MARKER, enum_key, step_name)

    # Then, we go and add the rest of the types
    with open(path_to_taskpanes, 'r') as f:
        code = f.read()
        code = code.replace(TASKPANEINFO_MARKER, f'| {OPEN_BRACKET}type: TaskpaneType.{enum_key}{CLOSE_BRACKET}\n     {TASKPANEINFO_MARKER}')
        if is_editing_taskpane:
            code = code.replace(EDITINGTASKPANE_MARKER, f'TaskpaneType.{enum_key},\n    {EDITINGTASKPANE_MARKER}')
        if is_remain_open_undo_redo_taskpane:
            code = code.replace(ALLOWUNDOREDOEDITINGTASKPANE_MARKER, f'TaskpaneType.{enum_key},\n    {ALLOWUNDOREDOEDITINGTASKPANE_MARKER}')

    with open(path_to_taskpanes, 'w') as f:
        f.write(code)


def get_curr_open_taskpane_code(original_step_name: str) -> None:
    taskpane_name = original_step_name.replace(' ', '') + 'Taskpane'
    taskpane_type = original_step_name.upper().replace(' ', '_')
    
    return f"""case TaskpaneType.{taskpane_type}: return (
                <{taskpane_name}
                    userProfile={OPEN_BRACKET}userProfile{CLOSE_BRACKET}
                    analysisData={OPEN_BRACKET}analysisData{CLOSE_BRACKET}
                    sheetDataArray={OPEN_BRACKET}sheetDataArray{CLOSE_BRACKET}
                    setUIState={OPEN_BRACKET}setUIState{CLOSE_BRACKET}
                    mitoAPI={OPEN_BRACKET}props.mitoAPI{CLOSE_BRACKET}
                    selectedSheetIndex={OPEN_BRACKET}uiState.selectedSheetIndex{CLOSE_BRACKET}
                />
            )
            {GETCURROPENTASKPANE_MARKER}"""

def write_to_mito(original_step_name: str) -> None:
    step_name_capital = original_step_name.replace(' ', '')
    path_to_mito = Path('./src/components/Mito.tsx')

    with open(path_to_mito, 'r') as f:
        code = f.read()
        code = code.replace(MITOIMPORT_MARKER, f'import {step_name_capital}Taskpane from \'./taskpanes/{step_name_capital}/{step_name_capital}Taskpane\';\n{MITOIMPORT_MARKER}')
        code = code.replace(GETCURROPENTASKPANE_MARKER, f'{(get_curr_open_taskpane_code(original_step_name))}')

    with open(path_to_mito, 'w') as f:
        f.write(code)


def write_new_taskpane(original_step_name: str, params: Dict[str, str], is_editing_taskpane: bool, is_live_updating_taskpane: bool, is_remain_open_undo_redo_taskpane: bool) -> None:
    
    step_name_capital = original_step_name.replace(' ', '')
    path_to_folder = Path('./src/components/taskpanes/') / step_name_capital
    path_to_taskpane = path_to_folder / f'{step_name_capital}Taskpane.tsx'

    # First, create the folder
    create_folder(path_to_folder)

    # Then, write the taskpane
    taskpane_code = get_new_taskpane_code(original_step_name, params, is_live_updating_taskpane)
    write_python_code_file(path_to_taskpane, taskpane_code)

    # Then, update the taskpane types file
    write_taskpane_types_file(original_step_name, is_editing_taskpane, is_remain_open_undo_redo_taskpane)

    # Then, update Mito.tsx
    write_to_mito(original_step_name)

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
    create_taskpane = input("Create a taskpane for this step? [y/n]").lower().startswith('y')
    is_editing_taskpane = create_taskpane and input('Is this a taskpane that should close if a toolbar button is pressed? [y/n]').lower().startswith('y')
    is_live_updating_taskpane = create_taskpane and input('Is this a live-updating taskpane? [y/n]').lower().startswith('y')
    is_remain_open_undo_redo_taskpane = create_taskpane and input('Is this a taskpane that can remain open if undo or redo are pressed? [y/n]').lower().startswith('y')

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
    write_steptype_to_types_file(original_step_name)
    print("Wrote step type to Types.tsx")
    write_to_api_file(original_step_name, params)
    print("Wrote to api.tsx")
    write_to_actions_file(original_step_name, params, create_taskpane)
    print("Wrote to actions")

    if create_taskpane:
        write_new_taskpane(original_step_name, params, is_editing_taskpane, is_live_updating_taskpane, is_remain_open_undo_redo_taskpane)
        print("Wrote new taskpane")
    else:
        print("Not writing taskpane...")



    # TODO:
    # 3. Be able to specify that we're creating a taskpane and then take the step parameters passed in a particular order and create a UI for them. For example, if sheet_index is the first param provided, then it should create a taskpane with a Dataframe -> DfName seletc.
    # 4. Be able to read the params back in correctly (and do some refactoring!)
    # 5. Be able to do upgrade refactoring automatically - just tell it how to migrate



if __name__ == "__main__":
    main()
