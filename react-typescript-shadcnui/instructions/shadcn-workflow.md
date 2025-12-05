---
description: "Workflow for driving AI development with shadcn/ui"
globs: ["*"]
type: "instructional-guide"
---

# Shadcn AI Development Workflow

## Step 1: Pre-requisites (CLI Actions)
*Note: AI cannot run terminal commands reliably. You must do this.*
"I have run the following commands:
- `npx shadcn@latest add button card input label form select dropdown-menu table`
- `npm install lucide-react react-hook-form zod @hookform/resolvers`
Assume these components exist in `@/components/ui`."

## Step 2: Foundation
*Prompt:* "Using the `RootLayout` prompt from my instructions, scaffold the main dashboard shell. Use `lucide-react` icons for the sidebar navigation (Home, Users, Settings)."

## Step 3: Feature Implementation
*Prompt:* "In the main content area, I need a 'Create User' feature. Use the 'Zod Form' recipe. The form should be inside a `<Card>`. The fields are Name, Email, and Role (Select component)."

## Step 4: Refinement
*Prompt:* "Refine the form. Add a `<Separator />` between the header and the form fields. Change the submit button to show a spinner (`lucide-react` Loader2) when `isSubmitting` is true."

## Step 5: Theming check
*Prompt:* "Review the color usage. Ensure we are using `bg-muted` for secondary backgrounds and `text-destructive` for error messages. Replace any hardcoded hex values with Tailwind semantic classes."