from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from app.config import settings
from app.schemas import (
    ChatRequest,
    ChatResponse,
    GuideGenerateRequest,
    GuideGenerateResponse,
    RoutePlanRequest,
    RoutePlanResponse,
    ASRResponse,
    SpotGuideRequest,
    SpotGuideResponse,
    SpotListResponse,
    TTSRequest,
    TTSResponse,
    VoiceChatResponse,
)
from app.services.guide_service import GuideService
from app.services.route_service import RouteService
from app.services.speech_service import SpeechService

app = FastAPI(title=settings.app_name, version="1.0.0")

route_service = RouteService()
guide_service = GuideService()
speech_service = SpeechService()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "env": settings.app_env}


@app.post("/api/v1/route/plan", response_model=RoutePlanResponse)
def plan_route(req: RoutePlanRequest) -> RoutePlanResponse:
    try:
        return route_service.plan(
            start_id=req.start_id,
            end_id=req.end_id,
            avoid_crowded=req.avoid_crowded,
            prefer_indoor=req.prefer_indoor,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/v1/guide/generate", response_model=GuideGenerateResponse)
async def generate_guide(req: GuideGenerateRequest) -> GuideGenerateResponse:
    if len(req.route_nodes) < 2:
        raise HTTPException(status_code=400, detail="route_nodes should contain at least 2 nodes")
    return await guide_service.generate(
        language=req.language,
        user_profile=req.user_profile,
        style=req.style,
        route_nodes=req.route_nodes,
    )


@app.get("/api/v1/spots", response_model=SpotListResponse)
def list_spots() -> SpotListResponse:
    return SpotListResponse(spots=guide_service.list_spots())


@app.post("/api/v1/guide/spot-generate", response_model=SpotGuideResponse)
async def generate_spot_guide(req: SpotGuideRequest) -> SpotGuideResponse:
    try:
        return await guide_service.generate_spot_guide(
            node_id=req.node_id,
            language=req.language,
            user_profile=req.user_profile,
            style=req.style,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/api/v1/session/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    answer = await guide_service.answer_question(
        question=req.question,
        language=req.language,
        current_spot=req.current_spot_id,
    )
    return ChatResponse(answer=answer)


@app.post("/api/v1/speech/tts", response_model=TTSResponse)
async def tts(req: TTSRequest) -> TTSResponse:
    audio_url, duration = await speech_service.tts(req.text, req.voice)
    return TTSResponse(audio_url=audio_url, duration_sec=duration)


@app.post("/api/v1/speech/asr", response_model=ASRResponse)
async def asr(
    audio: UploadFile = File(...),
    language: str = Form("zh"),
) -> ASRResponse:
    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="audio file is empty")
    text = await speech_service.asr(content, audio.filename or "voice.wav", language)
    return ASRResponse(text=text)


@app.post("/api/v1/session/voice-chat", response_model=VoiceChatResponse)
async def voice_chat(
    audio: UploadFile = File(...),
    language: str = Form("zh"),
    current_spot_id: str | None = Form(default=None),
) -> VoiceChatResponse:
    content = await audio.read()
    if not content:
        raise HTTPException(status_code=400, detail="audio file is empty")

    transcript = await speech_service.asr(content, audio.filename or "voice.wav", language)
    answer = await guide_service.answer_question(
        question=transcript,
        language=language,
        current_spot=current_spot_id,
    )
    return VoiceChatResponse(transcript=transcript, answer=answer)
