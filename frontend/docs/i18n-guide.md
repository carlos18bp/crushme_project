# i18n Implementation Guide

This guide explains how to use the internationalization (i18n) system in the project.

## Project Structure

```
src/
  ├── stores/
  │   └── modules/
  │       └── i18nStore.js    # Store for managing i18n state
  └── locales/
      ├── en.json            # English translations
      └── es.json            # Spanish translations
```

## How to Change Language

You can change the language in any component by using the i18n store:

```javascript
import { useI18nStore } from '@/stores/modules/i18nStore'

const i18nStore = useI18nStore()
i18nStore.setLocale('es') // for Spanish
i18nStore.setLocale('en') // for English
```

## Adding Translations

1. Add your translations in the corresponding JSON files under `src/locales/`:

```json
// en.json
{
  "welcome": "Welcome",
  "login": {
    "title": "Login",
    "email": "Email",
    "password": "Password"
  }
}

// es.json
{
  "welcome": "Bienvenido",
  "login": {
    "title": "Iniciar Sesión",
    "email": "Correo",
    "password": "Contraseña"
  }
}
```

## Using Translations

### In Vue Templates

```vue
<template>
  <!-- Simple translation -->
  <h1>{{ $t('welcome') }}</h1>

  <!-- Nested translation -->
  <h2>{{ $t('login.title') }}</h2>
  
  <!-- With parameters -->
  <p>{{ $t('hello', { name: username }) }}</p>
</template>
```

### In JavaScript/TypeScript

```javascript
import { useI18n } from 'vue-i18n'

export default {
  setup() {
    const { t } = useI18n()
    
    // Use translations in methods/computed
    const welcomeMessage = t('welcome')
    
    return {
      welcomeMessage
    }
  }
}
```

## Automatic Language Detection

The system includes automatic language detection based on the user's IP address. It will automatically set Spanish for users from Spanish-speaking countries and English for all others.

The language detection happens automatically when the i18n store is first initialized. You don't need to call any method manually - it just works!

If you need to force a language detection later (for example, after a user logs out), you can still do it manually:

```javascript
import { useI18nStore } from '@/stores/modules/i18nStore'

const i18nStore = useI18nStore()
await i18nStore.detectUserLanguage()
```

## URL-based Language Switching

The application supports language-based URLs. All routes are prefixed with the language code:

- English routes start with `/en/` (e.g., `/en/products`, `/en/cart`)
- Spanish routes start with `/es/` (e.g., `/es/products`, `/es/cart`)

The language will automatically switch based on the URL prefix. For example:
- Visiting `/es/products` will switch the language to Spanish
- Visiting `/en/products` will switch the language to English

When accessing the root URL (`/`), you will be automatically redirected to the appropriate language version based on:
1. Your previously selected language (if any)
2. Your detected country (if no previous selection)
3. English as the fallback

To programmatically navigate between languages, simply include the language code in your router navigation:

```javascript
// In your Vue component
import { useRouter } from 'vue-router'

const router = useRouter()

// Switch to Spanish version of current page
router.push('/es' + router.currentRoute.value.path.substring(3))

// Switch to English version of current page
router.push('/en' + router.currentRoute.value.path.substring(3))
```

## Important Notes

- Default language is set to English ('en')
- Language detection uses ipapi.co service
- Spanish is set for users from: Argentina, Bolivia, Chile, Colombia, Costa Rica, Cuba, Dominican Republic, Ecuador, El Salvador, Equatorial Guinea, Guatemala, Honduras, Mexico, Nicaragua, Panama, Paraguay, Peru, Spain, Uruguay, and Venezuela
- English is set for users from all other countries
- If the IP detection fails, it defaults to English
- Language preference is persisted between sessions
- If a translation is missing in the selected language, it will fallback to English
- Translations support nested objects for better organization
- The i18n configuration is in `src/stores/modules/i18nStore.js`
