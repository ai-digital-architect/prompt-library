---
description: "Master coding standards for Salt Design System (Salt DS)"
globs: 
  - "packages/**/*.{ts,tsx}"
  - "packages/**/*.css"
  - "site/**/*.{ts,tsx}"
triggers:
  - "salt ds"
  - "design system"
  - "react component"
---

# Salt Design System (Salt DS) Coding Standards

You are an expert React developer building applications using the **Salt Design System**. You must strictly adhere to the following rules when generating code for files matching `**/*.{tsx,ts,css}`.

## 1. Package Architecture (Monorepo Awareness)
- **Stable Components**: Import from `@salt-ds/core`.
  - *Context*: Located in `packages/core/src`. [cite_start]Includes `Button`, `Card`, `StackLayout`, `FlexLayout`, `GridLayout`, `Text`, `SaltProvider`[cite: 19, 52, 53, 62].
- **Experimental Components**: Import from `@salt-ds/lab`.
  - *Context*: Located in `packages/lab/src`. [cite_start]Includes `DatePicker`, `ComboBox`, `List`, `Tree`, `Badge`[cite: 467, 471, 475, 501].
- **Icons**: Import from `@salt-ds/icons`.
  - [cite_start]*Context*: Located in `packages/icons/src`[cite: 317].
  - Naming Convention: PascalCase (e.g., `AddDocument`, `ArrowRight`, `Search`).
- [cite_start]**Data Grid**: Use `ag-grid-react` combined with `@salt-ds/ag-grid-theme`[cite: 7].

## 2. Layout & Structure (Crucial)
- **Avoid** `<div>` or `<span>` for layout. Use Salt Layout components found in `@salt-ds/core`:
  - [cite_start]**`StackLayout`**: For 1D vertical/horizontal lists with consistent spacing (`gap`)[cite: 92].
  - [cite_start]**`FlexLayout`**: For 2D wrapping layouts or complex alignment (`justify`, `align`)[cite: 61].
  - [cite_start]**`GridLayout`**: For 12-column dashboard grids (`columns={12}`)[cite: 65].
  - [cite_start]**`BorderLayout`**: For application scaffolding (Header, Main, Footer, Sidebar)[cite: 51].
- [cite_start]**Root Provider**: All application trees must be wrapped in `<SaltProvider mode="light" density="medium">`[cite: 85].

## 3. Styling & Theming
- **No Hex Codes**: Never use hardcoded colors (e.g., `#FFFFFF`). Use Salt CSS variables.
  - Background: `var(--salt-container-primary-background)`
  - Text: `var(--salt-content-primary-foreground)`
  - Spacing: `var(--salt-spacing-100)` (multipliers of 8px).
- **Typography**: Do not use `<h1>`, `<h2>`. [cite_start]Use `<Text styleAs="h1">` or `<Display>` from `@salt-ds/core`[cite: 98].

## 4. Component Patterns
- [cite_start]**Forms**: Always wrap inputs (`Input`, `Checkbox`, `RadioButton`) in a `<FormField>` to handle accessibility, labels, and validation states automatically[cite: 63].
- **Cards**: Use `<Card>` for standard containers. [cite_start]Use `<InteractableCard>` if the entire card is clickable[cite: 66].
- [cite_start]**Buttons**: Prefer `sentiment="accented"` for primary actions and `sentiment="neutral"` for secondary[cite: 52].

## 5. Coding Style
- Use **TypeScript** for all components.
- Use functional components with hooks.
- Prefer `css` modules or `makeStyles` for custom styles, injecting Salt tokens.