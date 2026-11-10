from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import accounting, views
from .telegram_webhook import telegram_webhook

router = DefaultRouter()
router.register("destinations", views.DestinationViewSet)
router.register("tours", views.TourViewSet)
router.register("hotels", views.HotelViewSet)
router.register("food", views.FoodViewSet)
router.register("transport", views.TransportViewSet)
router.register("bookings", views.BookingViewSet, basename="booking")
router.register("saved", views.SavedItemViewSet, basename="saved")
router.register("messages", views.MessageAdminViewSet, basename="message")
router.register("partners", views.PartnerViewSet, basename="partner")
router.register("payments", accounting.PaymentViewSet, basename="payment")
router.register("promotions", views.PromotionViewSet, basename="promotion")
router.register("reviews", views.ReviewViewSet, basename="review")
router.register("legal", views.LegalPageViewSet, basename="legal")
router.register("expenses", accounting.ExpenseViewSet, basename="expense")

urlpatterns = [
    path("", include(router.urls)),
    path("site-content/", views.site_content),
    path("contact/", views.contact),
    path("newsletter/", views.newsletter),
    path("bookings-submit/", views.submit_booking),
    path("bookings-verify/", views.verify_booking_code),
    path("bookings-arrival/", views.booking_arrival),
    path("admin-stats/", views.admin_stats),
    path("customers/", views.customers),
    path("promotions-active/", views.active_promotions),
    path("accounting/summary/", accounting.summary),
    path("accounting/ledger/", accounting.ledger),
    path("accounting/rates/", accounting.rates),
    path("accounting/export/", accounting.export_csv),
    path("accounting/invoice/<int:pk>/", accounting.invoice),
    path("accounting/bookings/<int:pk>/", accounting.booking_finance),
    path("accounting/bookings/<int:pk>/auto-costs/", accounting.auto_costs),
    path("upload/", views.upload_image),
    path("texts/", views.site_texts),
    path("auth/register/", views.register),
    path("auth/login/", views.login),
    path("auth/logout/", views.logout),
    path("auth/me/", views.me),
    path("auth/credentials/", views.change_credentials),
    path("telegram/webhook/", telegram_webhook),
    path("deposits/octo/notify/", views.octo_notify),
    path("deposits/test/", views.test_payment),
]
