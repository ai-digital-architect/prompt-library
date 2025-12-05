---
description: "Prompts for scaffolding feature-based architecture"
globs: 
  - "src/**/*"
keywords: ["scaffold", "feature folder", "structure"]
---

# React Architecture Prompts

## Prompt: Scaffold New Feature
"Create a new feature module for '[Feature Name]'.
1. Create a folder `src/features/[feature-name]`.
2. Inside, create subfolders:
   - `api/`: For TanStack Query hooks (`useGet[Resource]`).
   - `components/`: For domain-specific UI.
   - `types/`: For TypeScript interfaces.
   - `routes/`: For defining the routes for this feature.
3. Create an `index.ts` file to export the public API of this feature (the main page component and routes)."

## Prompt: Setup Router (TanStack Router / React Router)
"Configure the application routing.
1. Create a `src/routes` folder.
2. Implement lazy loading for feature routes using `lazy(() => import(...))`.
3. Create a `AppRoutes` component that defines the main layout (Header/Sidebar) and renders `Outlet`.
4. Ensure a '404 Not Found' catch-all route is configured."