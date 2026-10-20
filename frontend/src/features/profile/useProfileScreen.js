import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  deleteAccount,
  fetchProfile,
  logout,
  removeAvatar,
  renameProfile,
  uploadAvatar,
} from '../../shared/api/backend/accountApi'
import { failureText } from '../../shared/api/failureText'
import { currentSession, endSession, updateIdentity } from '../../shared/session/authSession'
import { isSessionExpired } from '../../shared/session/authorizedRequest'
import { canDeleteAccount } from './logic/deleteGate'
import { nameRefusal } from './logic/profileView'
import { photoRefusal } from './logic/photoFile'
import { createRequestOrder } from './logic/requestOrder'

export function useProfileScreen() {
  const navigate = useNavigate()
  const [attempt, setAttempt] = useState(0)
  const [screen, setScreen] = useState({ status: 'loading' })
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState('')
  const [saving, setSaving] = useState(false)
  const [identityError, setIdentityError] = useState(null)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [deleteDraft, setDeleteDraft] = useState('')
  const [deleting, setDeleting] = useState(false)
  const [signingOut, setSigningOut] = useState(false)
  const names = useRef(createRequestOrder())
  const nameFlight = useRef(null)
  const photoLock = useRef(false)
  const deleteLock = useRef(false)
  const signOutLock = useRef(false)

  useEffect(() => {
    const controller = new AbortController()
    setScreen({ status: 'loading' })
    fetchProfile(controller.signal)
      .then((profile) => {
        if (controller.signal.aborted) return
        setScreen({ status: 'ready', profile })
        setDraft((current) => (current === '' ? profile.name : current))
      })
      .catch((error) => {
        if (controller.signal.aborted) return
        if (leaveIfExpired(error, navigate)) return
        setScreen({ status: 'error' })
      })
    return () => controller.abort()
  }, [attempt, navigate])

  function leaveIfExpired(error) {
    if (!isSessionExpired(error)) return false
    endSession()
    navigate('/', { replace: true })
    return true
  }

  function applyProfile(profile) {
    updateIdentity(profile.name, profile.avatar_url, profile.email)
    setScreen({ status: 'ready', profile })
  }

  async function saveName() {
    if (screen.status !== 'ready') return
    const refusal = nameRefusal(draft)
    if (refusal) {
      setIdentityError(refusal)
      return
    }
    if (nameFlight.current?.draft === draft) return
    const requestId = names.current.start()
    const sent = draft
    setSaving(true)
    setIdentityError(null)
    const promise = renameProfile(sent)
    nameFlight.current = { draft: sent, promise }
    try {
      const profile = await promise
      if (!names.current.accepts(requestId)) return
      applyProfile(profile)
      setDraft(profile.name)
      setEditing(false)
    } catch (error) {
      if (!names.current.accepts(requestId)) return
      if (leaveIfExpired(error)) return
      setIdentityError(failureText(error))
    } finally {
      if (names.current.accepts(requestId)) setSaving(false)
      if (nameFlight.current?.promise === promise) nameFlight.current = null
    }
  }

  async function pickPhoto(file) {
    const refusal = photoRefusal(file)
    if (refusal) {
      setIdentityError(refusal)
      return
    }
    if (photoLock.current || screen.status !== 'ready') return
    photoLock.current = true
    setIdentityError(null)
    try {
      applyProfile(await uploadAvatar(file))
    } catch (error) {
      if (leaveIfExpired(error)) return
      setIdentityError(failureText(error))
    } finally {
      photoLock.current = false
    }
  }

  async function dropPhoto() {
    if (photoLock.current || screen.status !== 'ready' || !screen.profile.avatar_url) return
    photoLock.current = true
    setIdentityError(null)
    try {
      applyProfile(await removeAvatar())
    } catch (error) {
      if (leaveIfExpired(error)) return
      setIdentityError(failureText(error))
    } finally {
      photoLock.current = false
    }
  }

  async function confirmDelete() {
    if (deleteLock.current || screen.status !== 'ready') return
    if (!canDeleteAccount(deleteDraft, screen.profile.email)) return
    deleteLock.current = true
    setDeleting(true)
    try {
      await deleteAccount()
      endSession()
      navigate('/account-deleted', { replace: true })
    } catch (error) {
      deleteLock.current = false
      setDeleting(false)
      if (leaveIfExpired(error)) return
      setIdentityError(failureText(error))
      setDeleteOpen(false)
    }
  }

  async function signOut() {
    if (signOutLock.current) return
    signOutLock.current = true
    setSigningOut(true)
    const session = currentSession()
    try {
      if (session) await logout(session.refreshToken)
    } catch {
      // Человек нажал «выйти»: уходим даже если сервер не ответил.
    }
    endSession()
    navigate('/', { replace: true })
  }

  const profile = screen.status === 'ready' ? screen.profile : null
  return {
    status: screen.status,
    profile,
    editing,
    draft,
    saving,
    identityError,
    deleteOpen,
    deleteDraft,
    deleting,
    signingOut,
    canDelete: profile ? canDeleteAccount(deleteDraft, profile.email) : false,
    retry: () => setAttempt((value) => value + 1),
    startEdit: () => {
      if (screen.status !== 'ready') return
      setDraft(screen.profile.name)
      setEditing(true)
    },
    setDraft,
    cancelEdit: () => {
      if (screen.status === 'ready') setDraft(screen.profile.name)
      setIdentityError(null)
      setEditing(false)
    },
    saveName,
    pickPhoto,
    dropPhoto,
    signOut,
    openDelete: () => {
      setDeleteDraft('')
      setDeleteOpen(true)
    },
    closeDelete: () => {
      if (deleting) return
      setDeleteOpen(false)
    },
    setDeleteDraft,
    confirmDelete,
  }
}
