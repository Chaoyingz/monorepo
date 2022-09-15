from typing import List, Optional

from mitosheet.code_chunks.code_chunk import CodeChunk
from mitosheet.step_performers.utils import get_param


class QueryCodeChunk(CodeChunk):

    def get_display_name(self) -> str:
        return 'Query'

    def get_description_comment(self) -> str:
        instrument = self.get_param('instruments')
        instrument_str = ",".join(instrument)
        return f'Query {instrument_str}'

    def get_code(self) -> List[str]:
        path: str = self.get_param('path')
        instruments: List[str] = self.get_param('instruments')
        fields: List[str] = self.get_param('fields')
        start_date: str = self.get_param('start_date')
        end_date: str = self.get_param('end_date')
        fields = [f"${field}" for field in fields]
        instrument_str = ",".join(instruments)
        code = ['import qlib']
        code += ['from qlib.data import D']
        code += [f'{instrument_str} = D.features({instruments}, {fields}, start_time="{start_date}", end_time="{end_date}").reset_index()']
        return code

    def get_created_sheet_indexes(self) -> List[int]:
        return []

    def combine_right(self, other_code_chunk: "CodeChunk") -> Optional["CodeChunk"]:

        return None
