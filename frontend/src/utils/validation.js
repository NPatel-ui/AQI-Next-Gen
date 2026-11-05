/**
 * Auth & Profile Validation Utilities
 */

export function validateEmail(email) {
  if (!email || typeof email !== 'string') {
    return 'Email address is required.';
  }
  const trimmed = email.trim();
  if (!trimmed.includes('@')) {
    return 'Email must contain an "@" symbol.';
  }
  const parts = trimmed.split('@');
  if (!parts[0] || !parts[1] || !parts[1].includes('.')) {
    return 'Please enter a complete email address (e.g. name@domain.com).';
  }
  return null;
}

export function validatePassword(password) {
  if (!password) {
    return 'Password is required.';
  }
  if (password.length < 6) {
    return 'Password must be at least 6 characters.';
  }
  if (!/[A-Z]/.test(password)) {
    return 'Password must contain at least 1 uppercase letter.';
  }
  if (!/[a-z]/.test(password)) {
    return 'Password must contain at least 1 lowercase letter.';
  }
  if (!/[0-9]/.test(password)) {
    return 'Password must contain at least 1 number.';
  }
  // At least 1 symbol
  if (!/[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`';]/.test(password)) {
    return 'Password must contain at least 1 symbol.';
  }
  return null;
}

export function getPasswordRuleStatus(password = '') {
  return {
    length: password.length >= 6,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    symbol: /[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`';]/.test(password),
  };
}

export function validateFullName(name) {
  if (!name || typeof name !== 'string') {
    return 'Full Name is required.';
  }
  const trimmed = name.trim();
  if (trimmed.length === 0) {
    return 'Full Name is required.';
  }

  // Only alphabets and spaces allowed
  if (!/^[a-zA-Z\s]+$/.test(trimmed)) {
    return 'In the Full Name only alphabets are allowed.';
  }

  // First alphabet must be Capital
  if (!/^[A-Z]/.test(trimmed)) {
    return 'First alphabet must be capital.';
  }

  if (trimmed.length < 2) {
    return 'Full Name must be at least 2 characters.';
  }

  return null;
}

