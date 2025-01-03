from pydantic import BaseModel
from typing import List
from typing import Optional

class Json_in_el(BaseModel):
    """
    Prediction input

    Machine_name and KPI_name (str): identifiers of the KPI to be predicted
    Date_prediction: number of days to forecast
    """
    Machine_Name: str
    KPI_Name: str
    Date_prediction: int

class Json_in(BaseModel):
    value: List[Json_in_el]

class LimeExplainationItem(BaseModel):
    date_info: str
    value: float

class Json_out_el(BaseModel):
    """
    The output of a prediction

    Machine_Name (str) and KPI_Name are the identifiers for the predicted series
    Predicted_value (List[flaot]): the list of the results
    Lower_bound, Upper_bound & confidence_score (List[float]): 
        each prediction has a "confidence_score chance to fall between "Lower_bound" and "Upper_bound"
    Lime_explaination (List[List[LimeExplainationItem]]): explaination of which components influence
      more the answer. For every prediction a list of (str,float) tuples are returned
    Measure_unit (str) the KPI's unit of measure
    Date_prediction (list[str]) date of the corresponding prediction
    Error_message (str): in case of error its description will be here
    Forecast (bool): forecast identifier
    Global_SHAP_values (Optional[List[List[float]]]): Matrix of shape (n_samples, n_features) containing
        global SHAP values for feature importance across all training samples
    """
    Machine_Name: str
    KPI_Name: str
    Predicted_value: Optional[List[float]]
    Lower_bound: List[float]
    Upper_bound: List[float]
    Confidence_score: List[float]
    Lime_explaination: List[List[LimeExplainationItem]]
    Measure_unit: str
    Date_prediction: List[str]
    Error_message: str
    Forecast: bool
    Global_SHAP_values: Optional[List[List[float]]] = None

class Json_out(BaseModel):
    value: List[Json_out_el]