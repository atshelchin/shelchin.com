+++
title = "Multiple Export Paths in SvelteKit Libraries"
date = 2025-10-15

+++



## The Challenge

When building a SvelteKit library, you might want to provide multiple import paths for better organization:

- `@shelchin/connectkit` - core utilities (JS/TS)
- `@shelchin/connectkit/connectors` - connector classes (JS/TS)
- `@shelchin/connectkit/components` - Svelte components

## The Solution

### 1. Directory Structure

```
src/lib/
├── index.ts                   # default export
├── connectors/
│   └── index.ts               # JS/TS exports
└── components/
    └── index.ts               # Svelte component exports
```

### 2. Package.json Configuration

The key is the `exports` field. Note that **only** the components path includes the `svelte` field:

```json
{
  "name": "@shelchin/connectkit",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "default": "./dist/index.js"
    },
    "./connectors": {
      "types": "./dist/connectors/index.d.ts",
      "default": "./dist/connectors/index.js"
    },
    "./components": {
      "types": "./dist/components/index.d.ts",
      "svelte": "./dist/components/index.js",
      "default": "./dist/components/index.js"
    }
  }
}
```

### 3. Usage

```typescript
// Core utilities (JS/TS)
import { createConnectKit } from '@shelchin/connectkit';

// Connectors (JS/TS)
import { MetaMaskConnector } from '@shelchin/connectkit/connectors';

// Svelte components
import { ConnectButton } from '@shelchin/connectkit/components';
```

## Key Takeaway

The `svelte` field in `exports` tells bundlers like Vite that the module contains Svelte components, enabling proper component preprocessing. For pure JS/TS modules, omit this field and use only `types` and `default`.

Build with `@sveltejs/package` and it handles the rest automatically.

**Pro tip**: This pattern works for any SvelteKit library mixing JS utilities and Svelte components!



------

**Related**: SvelteKit library, package exports, multiple entry points, npm package configuration

