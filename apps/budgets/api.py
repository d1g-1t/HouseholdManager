from ninja import Router
router = Router()

@router.get("/")
def list_budgets(request):

    return {"message": "Budgets API - coming soon"}
