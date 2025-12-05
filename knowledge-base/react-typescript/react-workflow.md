# React + TS Development Workflow

## Step 1: Feature Scaffolding
*User:* "Using the architecture prompts, scaffold a 'UserManagement' feature. It needs a list view and a details view."

## Step 2: Data Layer
*User:* "Create a data fetching solution for 'Users'. Use the TanStack Query recipe. The API endpoint is `/api/users`. Validate the response with Zod ensuring 'email' is a valid email string."

## Step 3: UI Implementation
*User:* "Create the 'UserList' component. Use a data table pattern. Import the `useUsers` hook we just created. Handle `isLoading` and `isError` states gracefully."

## Step 4: Logic Refinement
*User:* "I need a form to edit a user. Use the 'Type-Safe Form' recipe. Fields are Name (required) and Role (dropdown)."