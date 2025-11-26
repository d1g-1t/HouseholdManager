from ninja import Router
router = Router()

@router.get("/")
def get_analytics(request):

    return {"message": "Analytics API - coming soon"}
