# Week 5 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
### Automation A: Warp Drive saved prompts, rules, MCP servers

a. Design of each automation, including goals, inputs/outputs, steps
> TODO

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> TODO

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> TODO

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> TODO

e. How you used the automation (what pain point it resolves or accelerates)
> TODO



### Automation B: Multi‑agent workflows in Warp 

a. Design of each automation, including goals, inputs/outputs, steps
> TODO

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> TODO

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> TODO

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> TODO

e. How you used the automation (what pain point it resolves or accelerates)
> TODO


### (Optional) Automation C: Any Additional Automations
a. Design of each automation, including goals, inputs/outputs, steps
> TODO

b. Before vs. after (i.e. manual workflow vs. automated workflow)
> TODO

c. Autonomy levels used for each completed task (what code permissions, why, and how you supervised)
> TODO

d. (if applicable) Multi‑agent notes: roles, coordination strategy, and concurrency wins/risks/failures
> TODO

e. How you used the automation (what pain point it resolves or accelerates)
> TODO


## Implementation summary (code changes completed in this repo)

- **Task 7 – Robust error handling and response envelopes (easy–medium)**
  - Added Pydantic validation (`min_length=1`) to `NoteCreate` and `ActionItemCreate` in `backend/app/schemas.py` so empty titles, contents, and descriptions are rejected.
  - Introduced global FastAPI exception handlers in `backend/app/main.py` that return consistent JSON envelopes for errors:
    - Success: `{ "ok": true, "data": ... }`
    - Errors: `{ "ok": false, "error": { "code": "NOT_FOUND" | "BAD_REQUEST" | "HTTP_ERROR" | "VALIDATION_ERROR", "message": "...", ... } }`.
  - Updated `notes` and `action_items` routers to wrap all successful responses in the success envelope.
  - Updated backend tests in `backend/tests/test_notes.py` and `backend/tests/test_action_items.py` to assert the new envelope shape for both success and error cases.

- **Task 8 – Pagination for list endpoints (easy)**
  - Added `page` and `page_size` query parameters and pagination logic to `GET /notes` and `GET /action-items`, returning `items`, `total`, `page`, and `page_size` inside the success envelope.
  - Capped `page_size` to a maximum value and ensured that out‑of‑range pages return an empty `items` list but still report the correct `total`.
  - Implemented pagination tests for action items in `backend/tests/test_action_items.py` to cover clamped `page_size` and an empty last page.

- **Frontend updates (supporting the above tasks + extra UX)**
  - Updated `frontend/index.html` to add pagination controls (Prev/Next buttons and `Page X of Y` indicators) under both the Notes and Action Items lists.
  - Updated `frontend/app.js` to:
    - Use a shared `fetchJSON` helper that expects the `{ ok, data }` envelope from the backend.
    - Request paginated data for notes and action items, render the current page, and enable/disable pagination buttons appropriately.
  - Added a small UX feature to show the most recently created entities:
    - `Last added note` and `Last added action item` text under each form, populated directly from the POST responses to `/notes/` and `/action-items/`.

You (the student) should still fill in the Name, SUNet ID, citations, time spent, and detailed Warp automation sections above to describe how you used Warp Drive and multi‑agent workflows.
