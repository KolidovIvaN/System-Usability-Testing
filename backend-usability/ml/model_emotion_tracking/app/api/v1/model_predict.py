from fastapi import APIRouter, Request, HTTPException, status

from app.api.schemas.predict import ModelRequest, PredictionResult

router = APIRouter()


@router.post("/predict")
async def model_predict(
    request: Request,
    model_request: ModelRequest,
):
    
    try:
        processed_data = await request.app.state.preprocessing.preprocessing_images(
            data_user_face=model_request.data_user_face
        )
    
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={f"Error preprocessing data: {e}"})
    
    try:
        results_model = await request.app.state.model.predict_emotion(
            img_face=processed_data.get("face")
        )
    
        return PredictionResult(
            emotions=results_model
        )
        
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={f"Error model prediction: {e}"})