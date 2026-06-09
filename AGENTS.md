# Agent Instructions

These rules apply to all current and future agents working in this repository.

## Communication

- Talk with the user in Czech by default.
- If the user uses another language, follow the user's language.
- Write project documentation in simple English.
- Keep documentation short and mostly in bullet points.
- Use normal sentences when they make the meaning clearer than bullet lists.

## Repository Boundaries

- Work only inside this repository directory.
- Do not read or write files outside this repository.
- Do not create commits.
- Do not create branches.
- Do not open pull requests.
- Do not run git write operations.
- Allowed git commands are read-only commands, for example:
  - `git status`
  - `git diff`
  - `git log`
  - `git show`

## Guide Structure

- This repository contains multiple personal learning guides.
- Put guide-specific content inside the guide folder, for example `dbt/`.
- Build each guide in small steps.
- Use short step directory names, for example:
  - `steps/01-init`
  - `steps/02-staging`
- Each step should contain a short markdown guide and any files needed for that step.
- Do not overbuild future steps.

## Step Style

- Keep steps practical and focused on learning.
- A step may contain multiple related concepts when they belong together.
- Use sections only when they add new value.
- Use `Experiment: ...` for practical hands-on sections when it reads better than separate `Files` and `Run` sections.
- Prefer clear section names such as:
  - `Goal`
  - `Knowledge: ...`
  - `Experiment: ...`
  - `Files`
  - `Run`
  - `Test`
  - `Checks`
  - `Design`
  - `Warning`
  - `Navigation`
- Do not add recap sections like `What We Learned`.
- Do not repeat setup or run instructions from earlier steps unless they changed.
- Do not repeat summaries of earlier lessons.
- Do not force every explanation into bullets; short paragraphs are fine for knowledge and examples.
- Put short example code directly inside the markdown step.
- Do not create a duplicate example file next to the markdown if the full code is already shown.
- Use extra files only when the step really needs multiple files.
- Merge practical sections when separate headings would only add noise.
- Keep CLI checks short and relevant to the learning topic.
- Use precise wording for learner actions, for example `inspect` when the learner only observes values, and `try/change` only when they should edit or experiment.
- Avoid troubleshooting-heavy content unless the step is explicitly about troubleshooting.
- Mention local runtime behavior only where it changes how the learner runs the step.

## Secrets

- Never write real secrets or credentials.
- Use placeholders only when secrets become needed.
