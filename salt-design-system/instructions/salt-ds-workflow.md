---
description: "Step-by-step workflow for driving AI development with Salt DS"
globs: ["*"]
type: "instructional-guide"
---

# Salt DS AI Development Workflow

## Step 1: Initialization
*Action:* Start every session by validating the **System Instructions** are active. If not, paste the content of `.github/copilot-instructions.md`.

## Step 2: Foundation Layout
*Prompt:* "Using the Salt DS instructions, scaffold a new page for 'Analytics Dashboard'. Use a Border Layout with a fixed sidebar and fluid main content. Ensure `SaltProvider` is at the root."

## Step 3: Component Injection
*Prompt:* "In the main content area, add a 'KPI Section'. Use a GridLayout with 4 columns. Inside each, place a Card displaying a metric. Use the Salt Metric pattern if available, otherwise compose it using Display and Text components from `@salt-ds/core`."

## Step 4: Refinement (Theming)
*Prompt:* "Refine the Sidebar. Instead of a simple list, use the `StackLayout` with `Button` components (variant='secondary', fullWidth). Add icons from `@salt-ds/icons` to each button (Home, Analytics, Settings)."

## Step 5: QA & Accessibility
*Prompt:* "Review the 'Registration Form' code. Ensure all inputs are wrapped in `FormField` for accessibility and that we are using Salt design tokens for spacing, not hardcoded pixels."