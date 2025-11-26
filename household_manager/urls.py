from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from ninja import NinjaAPI

from apps.analytics.api import router as analytics_router
from apps.budgets.api import router as budgets_router
from apps.categories.api import router as categories_router
from apps.expenses.api import router as expenses_router
from apps.families.api import router as families_router
from apps.receipts.api import router as receipts_router
from apps.telegram_bot.api import router as telegram_router
from apps.users.api import router as users_router

api = NinjaAPI(
    title="HouseholdManager API",
    version="1.0.0",
    description="Advanced Family Budget Manager with OCR, ML categorization, and Real-time updates",
    docs_url="/api/docs",
)

api.add_router("/users", users_router, tags=["Users"])
api.add_router("/families", families_router, tags=["Families"])
api.add_router("/expenses", expenses_router, tags=["Expenses"])
api.add_router("/receipts", receipts_router, tags=["Receipts"])
api.add_router("/budgets", budgets_router, tags=["Budgets"])
api.add_router("/categories", categories_router, tags=["Categories"])
api.add_router("/analytics", analytics_router, tags=["Analytics"])
api.add_router("/telegram", telegram_router, tags=["Telegram"])

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("", include("django_prometheus.urls")),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = "HouseholdManager Administration"
admin.site.site_title = "HouseholdManager Admin"
admin.site.index_title = "Welcome to HouseholdManager Administration"
