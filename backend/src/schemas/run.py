from pydantic import BaseModel, Field, ConfigDict
from typing import Literal

class RunInput(BaseModel):
 model_config=ConfigDict(allow_inf_nan=False, str_strip_whitespace=True)
 study_id:int=Field(gt=0)
 name:str=Field(min_length=2, max_length=180)
 bootstrap_repeats:int=Field(ge=400, le=1000, strict=True)
 seed:int=Field(ge=0, le=1000000000, strict=True)
 panel_scope:Literal['fixed_three_raters']='fixed_three_raters'
 category_merge:dict[str, str]|None=Field(default=None, description='可选：原类别→归并类别的完整映射；须覆盖全部声明类别且归并后至少2类')
