/**
 * Extrait un message d'erreur lisible depuis une réponse API DRF.
 * Unifie la gestion des erreurs dans tous les catch() du frontend.
 *
 * @param {Error} err - L'erreur axios
 * @param {string} fallback - Message par défaut si aucun message extractable
 * @returns {string} Message d'erreur lisible
 *
 * @example
 * } catch (err) {
 *   toast.error(handleApiError(err, 'Impossible de créer le patient.'))
 * }
 */
export function handleApiError(err, fallback = 'Une erreur est survenue.') {
  const data = err?.response?.data

  if (!data) {
    // Pas de réponse du serveur (réseau, timeout, etc.)
    if (err?.code === 'ECONNABORTED') return 'La requête a expiré. Vérifiez votre connexion.'
    if (!err?.response) return 'Impossible de contacter le serveur.'
    return fallback
  }

  // DRF peut retourner : string, { detail: "..." }, { field: ["msg"] }, { non_field_errors: [...] }
  if (typeof data === 'string') return data
  if (typeof data.detail === 'string') return data.detail

  // Erreurs de validation de champs
  const firstField = Object.entries(data).find(([, v]) => v)
  if (firstField) {
    const [field, msgs] = firstField
    const msg = Array.isArray(msgs) ? msgs[0] : msgs
    if (typeof msg === 'string') {
      // Capitaliser le nom du champ pour l'affichage
      const fieldName = field === 'non_field_errors' ? '' : `${field} : `
      return `${fieldName}${msg}`
    }
  }

  return fallback
}
