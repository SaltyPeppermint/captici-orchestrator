from typing import Dict, List, Optional

from pydantic.main import BaseModel


class TestResponse(BaseModel):
    individual_results: Dict[int, Optional[float]]
    is_regression: bool
    regressing_config: Optional[List[int]] = None
