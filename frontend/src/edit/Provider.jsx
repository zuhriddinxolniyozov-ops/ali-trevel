import { useCallback, useMemo, useState } from 'react'
import { useAuth } from '../hooks'
import Bridge from './Bridge'
import { EDIT_SESSION, EditContext } from './context'

/** Turns the editing tools on, but only inside the admin's site-editor frame and only for a signed-in admin. */
export function EditProvider({ children }) {
  const { user } = useAuth()
  const enabled = EDIT_SESSION && user?.role === 'admin'
  const [mode, setMode] = useState('edit')
  const [version, setVersion] = useState(0)
  const [modal, setModal] = useState(null) // { resource, slug|null, preset|null }
  const bump = useCallback(() => setVersion((v) => v + 1), [])
  const openRecord = useCallback((resource, slug = null, preset = null) => setModal({ resource, slug, preset }), [])
  const closeModal = useCallback(() => setModal(null), [])

  const value = useMemo(() => ({
    enabled, mode: enabled ? mode : 'browse', editing: enabled && mode === 'edit',
    version, bump, setMode, modal, openRecord, closeModal,
  }), [enabled, mode, version, bump, modal, openRecord, closeModal])

  return <EditContext.Provider value={value}>{children}{enabled && <Bridge />}</EditContext.Provider>
}
