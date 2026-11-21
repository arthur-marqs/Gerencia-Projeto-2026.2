export const SESSION_EXPIRED_EVENT = 'setupflow:session-expired'

export async function apiFetch(
  input: RequestInfo | URL,
  init?: RequestInit,
): Promise<Response> {
  const response = await fetch(input, init)

  if (response.status === 401) {
    window.dispatchEvent(new Event(SESSION_EXPIRED_EVENT))
  }

  return response
}