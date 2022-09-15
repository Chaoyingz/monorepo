from typing import Dict, Any, List, Set, Tuple

import pandas as pd
import qlib
from qlib.data import D
from mypy.applytype import Optional

from mitosheet.code_chunks.code_chunk import CodeChunk
from mitosheet.code_chunks.empty_code_chunk import EmptyCodeChunk
from mitosheet.code_chunks.step_performers.query_code_chunk import QueryCodeChunk
from mitosheet.state import State, DATAFRAME_SOURCE_IMPORTED
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.step_performers.utils import get_param


class QueryStepPerformer(StepPerformer):
    """
    Query data from local database
    """

    @classmethod
    def step_version(cls) -> int:
        return 1

    @classmethod
    def step_type(cls) -> str:
        return 'query'

    @classmethod
    def execute(cls, prev_state: State, params: Dict[str, Any]) -> Tuple[State, Optional[Dict[str, Any]]]:
        path: str = get_param(params, 'path')
        instruments: List[str] = get_param(params, 'instruments')
        fields: List[str] = get_param(params, 'fields')
        start_date: str = get_param(params, 'start_date')
        end_date: str = get_param(params, 'end_date')
        fields = [f"${field}" for field in fields]

        use_deprecated_id_algorithm: bool = get_param(params, 'use_deprecated_id_algorithm') if get_param(params, 'use_deprecated_id_algorithm') else False

        qlib.init(provider_uri=path)
        df = D.features(instruments, fields, start_time=start_date, end_time=end_date)
        df.reset_index(inplace=True)
        # Create a new step
        post_state = prev_state.copy()
        post_state.add_df_to_state(
            df,
            DATAFRAME_SOURCE_IMPORTED,
            df_name=",".join(instruments),
            use_deprecated_id_algorithm=use_deprecated_id_algorithm
        )

        return post_state, {}

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        post_state: State,
        params: Dict[str, Any],
        execution_data: Optional[Dict[str, Any]],
    ) -> List[CodeChunk]:
        return [
            QueryCodeChunk(prev_state, post_state, params, execution_data)
        ]

    @classmethod
    def get_modified_dataframe_indexes(cls, params: Dict[str, Any]) -> Set[int]:
        return {-1}
