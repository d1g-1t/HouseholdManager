from ninja import Router
router = Router()

@router.post("/webhook")
def telegram_webhook(request):

    return {"message": "Telegram webhook - coming soon"}
