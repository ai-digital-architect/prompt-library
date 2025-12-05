---
description: "Recipes for Data Fetching, Forms, and Logic patterns"
globs: 
  - "src/features/**/*"
keywords: ["react-query", "zod", "form", "hook"]
---

# React Solution Recipes

## Prompt: Data Fetching (TanStack Query)
"Create a custom data fetching hook for '[Resource Name]'.
1. Import `useQuery` from `@tanstack/react-query`.
2. Define a fetch function using `axios` or `fetch`.
3. Define a **Zod Schema** to validate the API response. Parse the response data with this schema inside the fetch function.
4. Create the hook `use[Resource]`.
5. Return the query object. Ensure `queryKey` is strongly typed and follows the pattern `['entity', 'list', filters]`."

## Prompt: Type-Safe Form (RHF + Zod)
"Build a form for '[Form Name]' using React Hook Form and Zod.
1. Define a Zod schema `formSchema` with validation rules (email, min length).
2. Infer the TypeScript type `FormValues` from the schema.
3. Use the `useForm<FormValues>` hook with `zodResolver`.
4. Create the UI using controlled inputs (via `register` or `Controller`).
5. Handle submission with a function that accepts `FormValues`."

## Prompt: Compound Component Pattern
"Refactor the `[Component Name]` into a Compound Component pattern.
1. Create a Context to share state between children (e.g., `ToggleContext`).
2. Create sub-components: `Root`, `Trigger`, `Content`.
3. Export them attached to the Root (e.g., `Accordion.Item`).
4. Ensure accessibility attributes (ARIA) are handled automatically in the sub-components."