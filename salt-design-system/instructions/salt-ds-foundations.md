---
description: "Prompts for scaffolding application layouts using Salt DS"
globs: 
  - "src/App.tsx"
  - "src/layouts/**/*"
keywords: ["scaffold", "layout", "grid", "border layout"]
---

# Salt DS Foundation Prompts

## Prompt: App Scaffolding
"Create a root application structure using Salt Design System.
1. [cite_start]Import `SaltProvider` and `BorderLayout` from `@salt-ds/core`[cite: 19, 51].
2. Wrap the app in `SaltProvider`.
3. Create a main layout using `BorderLayout`:
   - **Header**: Use a `<header>` tag containing a `StackLayout` (horizontal) with a Logo and Navigation.
   - **Main**: A central content area.
   - **Footer**: A footer with copyright text.
4. Ensure the theme is set to 'light' and density to 'medium'."

## Prompt: Dashboard Grid Layout
[cite_start]"Generate a dashboard layout using `GridLayout` from `@salt-ds/core`[cite: 65].
- The grid should have 12 columns.
- **Gap**: Use a spacing of 3 (`var(--salt-spacing-300)`).
- **Item 1 (Sidebar)**: Spans 2 columns using `GridItem`.
- **Item 2 (Main Chart)**: Spans 10 columns and 2 rows.
- **Item 3 (Metrics)**: Create a row of 4 cards below the main chart, each spanning 3 columns.
- [cite_start]Use `GridItem` for each section[cite: 64]."