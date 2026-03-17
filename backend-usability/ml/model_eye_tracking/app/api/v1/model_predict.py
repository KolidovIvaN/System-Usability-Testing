import time

from fastapi import APIRouter, Request, HTTPException, status

from app.api.schemas.predict import ModelRequest, PredictionResult
from app.utils.logger import get_logger


router = APIRouter()
logger = get_logger("predict_endpoint")


@router.post("/predict", response_model=PredictionResult)
async def model_predict(
    request: Request,
    model_request: ModelRequest,
):
    start_total_time = time.time()
    logger.info(f"Received prediction request")
    
    try:
        processed_data = await request.app.state.preprocessing_pool.process(
            data_user_face=model_request.data_user_face
        )
        logger.debug(f"Preprocessing completed: time {time.time() - start_total_time:.3f}s")
    
    except Exception as e:
        logger.error(f"Preprocessing error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Preprocessing failed", "message": str(e)}
        )
    
    try:
        predict_time_start = time.time()
        results_model = await request.app.state.model_pool.predict(data=processed_data)
        
        logger.info(f"Prediction completed: total_time {time.time() - predict_time_start:.3f}s")
        
        total_time = time.time() - start_total_time
        logger.info(f"Full request processing time: {total_time:.3f}s")
    
        return PredictionResult(eye_coordinates=results_model)
        
    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Model prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Model prediction failed", "message": str(e)}
        )