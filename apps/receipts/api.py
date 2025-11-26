from ninja import Router
router = Router()

@router.get("/")
def list_receipts(request):

    return {"message": "Receipts API - coming soon"}
