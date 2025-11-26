from ninja import Router
router = Router()

@router.get("/")
def list_expenses(request):

    return {"message": "Expenses API - coming soon"}
