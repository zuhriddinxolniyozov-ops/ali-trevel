import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import './index.css'
import { AuthProvider } from './hooks'
import { I18nProvider } from './i18n'
import { EditProvider } from './edit/Provider'
import Layout from './components/Layout'
import Home from './pages/Home'
import { DestinationDetail, Destinations, Food, HotelDetail, Hotels, TourDetail, Tours, Transport } from './pages/Catalog'
import { About, Contact } from './pages/Info'
import Legal from './pages/Legal'
import Plan from './pages/Plan'
import { Account, Login, Register, RequireAuth } from './pages/Auth'
import { PartnerDashboard, PartnerRegister, PartnersHome } from './pages/Partners'
import { EmptyState } from './components/ui'
import AdminLayout from './admin/AdminLayout'
import { Bookings, Customers, Enquiries, Overview, Partners, Settings } from './admin/Pages'
import { AdminListings, AdminTours } from './admin/Catalogs'
import Content from './admin/Content'
import SiteEditor from './admin/SiteEditor'
import Accounting from './admin/Accounting'
import Promotions from './admin/Promotions'
import Reviews from './admin/Reviews'
import GroupPricing from './admin/GroupPricing'
import LegalAdmin from './admin/LegalAdmin'
import PartnerDocs from './admin/PartnerDocs'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <I18nProvider>
        <AuthProvider>
          <EditProvider>
          <Routes>
            <Route path="/admin" element={<RequireAuth admin><AdminLayout /></RequireAuth>}>
              <Route index element={<Overview />} />
              <Route path="site" element={<SiteEditor />} />
              <Route path="accounting" element={<Accounting />} />
              <Route path="promotions" element={<Promotions />} />
              <Route path="reviews" element={<Reviews />} />
              <Route path="group-pricing" element={<GroupPricing />} />
              <Route path="legal" element={<LegalAdmin />} />
              <Route path="partner-letters" element={<PartnerDocs />} />
              <Route path="tours" element={<AdminTours />} />
              <Route path="listings" element={<AdminListings />} />
              <Route path="bookings" element={<Bookings />} />
              <Route path="customers" element={<Customers />} />
              <Route path="partners" element={<Partners />} />
              <Route path="enquiries" element={<Enquiries />} />
              <Route path="content" element={<Content />} />
              <Route path="settings" element={<Settings />} />
            </Route>
            <Route element={<Layout />}>
              <Route path="/" element={<Home />} />
              <Route path="/destinations" element={<Destinations />} />
              <Route path="/destinations/:slug" element={<DestinationDetail />} />
              <Route path="/tours" element={<Tours />} />
              <Route path="/tours/:slug" element={<TourDetail />} />
              <Route path="/hotels" element={<Hotels />} />
              <Route path="/hotels/:slug" element={<HotelDetail />} />
              <Route path="/food" element={<Food />} />
              <Route path="/transport" element={<Transport />} />
              <Route path="/plan" element={<Plan />} />
              <Route path="/about" element={<About />} />
              <Route path="/contact" element={<Contact />} />
              <Route path="/legal/:page" element={<Legal />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/account" element={<RequireAuth><Account /></RequireAuth>} />
              <Route path="/partners" element={<PartnersHome />} />
              <Route path="/partners/register" element={<PartnerRegister />} />
              <Route path="/partners/dashboard" element={<RequireAuth><PartnerDashboard /></RequireAuth>} />
              <Route path="*" element={<div className="shell py-24"><EmptyState title="Page not found" /></div>} />
            </Route>
          </Routes>
          </EditProvider>
        </AuthProvider>
      </I18nProvider>
    </BrowserRouter>
  </React.StrictMode>,
)
