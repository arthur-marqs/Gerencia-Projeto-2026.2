export type LoginErrors = {
  email?: string
  password?: string
}

export function validateLogin(email: string, password: string): LoginErrors {
  const errors: LoginErrors = {}
  const normalizedEmail = email.trim()

  if (!normalizedEmail) {
    errors.email = 'Informe seu e-mail.'
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) {
    errors.email = 'Informe um e-mail válido.'
  }

  if (!password) {
    errors.password = 'Informe sua senha.'
  }

  return errors
}