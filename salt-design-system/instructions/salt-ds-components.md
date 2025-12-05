---
description: "Recipes for implementing specific Salt DS components correctly"
globs: 
  - "src/components/**/*"
  - "src/features/**/*"
keywords: ["form", "ag-grid", "card", "pattern"]
---

# Salt DS Component Prompts

## Prompt: Data Entry Form
"Create a 'User Registration Form' component.
- [cite_start]Use a `StackLayout` (vertical, gap=3) as the container[cite: 92].
- **Fields**:
  1. [cite_start]**Name**: `Input` wrapped in `FormField` (Label: 'Full Name')[cite: 63].
  2. [cite_start]**Role**: `Dropdown` (from Lab) wrapped in `FormField` (Label: 'Role', Options: Admin, User, Viewer)[cite: 59].
  3. [cite_start]**Preferences**: `CheckboxGroup` wrapped in `FormField` (Label: 'Notifications')[cite: 53].
- **Validation**: Add a generic error state to the Name field using `validationStatus='error'` on the `FormField`.
- [cite_start]**Actions**: A `FlexLayout` at the bottom with 'Cancel' (Neutral Button) and 'Register' (Accented Button)[cite: 52]."

## Prompt: Data Grid (Ag-Grid)
"Implement a Data Grid using `ag-grid-react` styled with Salt.
1. [cite_start]Import styles from `@salt-ds/ag-grid-theme/salt-ag-theme.css`[cite: 8].
2. Wrap the grid in a `div` with className `ag-theme-salt-variant-primary`.
3. Define 3 columns: ID, Name, Status.
4. Use dummy JSON data for rows.
5. Ensure the grid takes 100% height of its container."

## Prompt: Status Card Pattern
"Build a 'System Status' card using Salt Core.
- [cite_start]Use `<Card>` with `accent='left'`[cite: 53].
- Inside, use a `StackLayout`.
- [cite_start]**Header**: `FlexLayout` with a `<StatusIndicator status='success'>` and a generic title `<Text styleAs='h3'>`[cite: 140, 98].
- **Body**: `<Text>` describing the server uptime.
- [cite_start]**Footer**: `<Link>` to 'View Logs'[cite: 68]."