import { createContext, useContext } from 'react'

/**
 * The site editor shows the public site inside the admin console (an iframe pointing at `/?edit=1`).
 * Edit tools only exist in that frame, and only for a signed-in admin; everywhere else this context is inert.
 */
export const EDIT_SESSION = (() => {
  try {
    if (window.self === window.top) return false
    const asked = new URLSearchParams(window.location.search).get('edit') === '1'
    if (asked) sessionStorage.setItem('ali-edit', '1')
    return asked || sessionStorage.getItem('ali-edit') === '1'
  } catch { return false }
})()

export const EditContext = createContext({
  enabled: false, editing: false, mode: 'browse', version: 0,
  bump: () => {}, setMode: () => {}, openRecord: () => {}, closeModal: () => {}, modal: null,
})

export const useEdit = () => useContext(EditContext)
