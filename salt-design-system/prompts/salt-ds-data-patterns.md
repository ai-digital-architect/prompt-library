---
description: "Recipes for complex data interfaces and Ag-Grid integration in Salt DS"
globs: 
  - "src/**/grid/**/*"
  - "src/**/table/**/*"
  - "src/features/dashboard/**/*"
keywords: ["ag-grid", "data grid", "table", "complex data", "master detail"]
---

# Salt DS Data Pattern Prompts

## Context: Grid Strategy
*Note: Salt DS supports two grid types. Use the prompts below based on the requirement.*
1.  **Salt Data Grid (`@salt-ds/data-grid`)**: For native, lightweight, accessible grids consistent with Salt Core.
2.  **Ag-Grid Theme (`@salt-ds/ag-grid-theme`)**: For enterprise-grade features (pivoting, vast datasets, complex filtering) styled to match Salt.

---

## Prompt: Ag-Grid Standard Setup
"Implement a data grid using `ag-grid-react` with the Salt Design System theme.
1.  **Imports**:
    -   Import `AgGridReact` from `ag-grid-react`.
    -   Import the Salt theme CSS: `@salt-ds/ag-grid-theme/salt-ag-theme.css`.
    -   Import `ag-grid-community/styles/ag-grid.css` and `ag-grid-community/styles/ag-theme-alpine.css` (or base styles) if required by your version.
2.  **Container Class**: Wrap the grid in a generic `div` with the class `ag-theme-salt-variant-primary` (or `secondary`/`zebra` for variants).
3.  **Density Handling**:
    -   Apply density classes dynamically based on the app state: `ag-theme-salt-density-medium` (default), `high`, `low`, or `touch`.
    -   Ensure the container has a defined height (e.g., `height: 500px` or `100%`) as Ag-Grid requires it.
4.  **Columns**: Define column definitions with `headerName` and `field`.
5.  **Data**: Use standard row data arrays."

## Prompt: Ag-Grid with Custom Salt Renderers
"Create an Ag-Grid instance that uses Salt components inside the cells.
1.  **Status Column**: Create a component `StatusRenderer`. Inside, use the `<StatusIndicator>` and `<Text>` from `@salt-ds/core` wrapped in a `FlexLayout` with `gap={1}`.
2.  **Action Column**: Create a component `ActionRenderer`. Inside, use a `Button` (variant='secondary') with an icon from `@salt-ds/icons` (e.g., `EditIcon`).
3.  **Grid Options**: Register these components in the `components` prop of `AgGridReact` or use them directly in `cellRenderer` inside column definitions.
4.  **Row Height**: Ensure `rowHeight` matches the Salt density token (e.g., 48px for medium) or use `getRowHeight` to adapt dynamically."

## Prompt: Salt Native Data Grid (Lightweight)
"Implement a read-only table using the native Salt Data Grid.
1.  [cite_start]**Import**: Use components from `@salt-ds/data-grid`[cite: 297].
    -   `Grid`, `GridColumn`, `GridHeader`, `GridBody`, `GridRow`, `GridCell`.
2.  **Structure**:
    -   Define the `<Grid>` component.
    -   Map your data to `<GridRow>` and `<GridCell>`.
3.  **Styling**: Use the `aria-rowindex` and `aria-colindex` props for accessibility if handling large sets manually.
4.  **Selection**: If row selection is needed, stick to the standard 'single' or 'multi' select modes provided by the hook `useSelection` from the package."