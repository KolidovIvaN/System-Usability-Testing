import logging
import os

from fastapi import APIRouter, Request, HTTPException, status

from app.api.schemas.predict import ModelRequest, PredictionResult


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/predict", response_model=PredictionResult)
async def model_predict(
    request: Request,
    model_request: ModelRequest,
):

    logger.info(
        f"Prediction request received | "
        f"User data keys: {list(model_request.data_user_face.keys())}"
    )
    
    try:
        processed_data = await request.app.state.preprocessing.preprocessing_images(
            data_user_face=model_request.data_user_face
        )

    except Exception as e:
        logger.error(f"Preprocessing failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error preprocessing data: {str(e)}"
        )
    
    try:
        results_model = await request.app.state.model_pool.predict(
            img_face=processed_data["face"]
        )
        
        logger.info(
            f"Prediction completed | "
            f"Results: {results_model}"
        )
        
        return PredictionResult(emotions=results_model)
        
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Model prediction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error model prediction: {str(e)}"
        )