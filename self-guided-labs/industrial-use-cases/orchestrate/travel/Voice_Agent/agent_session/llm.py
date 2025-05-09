from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models import ModelInference
import os
from dotenv import load_dotenv

load_dotenv(override=True)

def init_watsonx_llm(model_id = 'mistralai/mistral-large'):

    credentials = Credentials(
        url=os.getenv("WX_URL"),
        api_key=os.getenv("WX_API_KEY")
    )

    # model_id = 'mistralai/mistral-large'

    model_parameters = {
        GenParams.DECODING_METHOD: "greedy",
        GenParams.MAX_NEW_TOKENS: 4000,
        GenParams.STOP_SEQUENCES: ["PAUSE"]
    }

    watsonx_llm = ModelInference(
        model_id=model_id, 
        params=model_parameters, 
        credentials=credentials,
        project_id=os.getenv("WX_PROJECT_ID")
    )

    return watsonx_llm