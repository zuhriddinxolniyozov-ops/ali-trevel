from django.contrib import admin

from . import models

for model in (
    models.SiteContent, models.Destination, models.Tour, models.Hotel, models.FoodExperience,
    models.TransportOption, models.BookingRequest, models.ContactMessage,
    models.NewsletterSubscriber, models.SavedItem, models.Partner, models.Promotion, models.LegalPage,
):
    admin.site.register(model)
