# Preferences

## Basics

- Timezone: US/Eastern (EST/EDT)
- Working hours: Mon–Fri, 9:00–20:00
- Preferred units: imperial
- Preferred spelling: US

## Default response style

- Concision: concise
- Structure: bullets first
- Dates: always use exact dates (e.g., 2026-03-03) when scheduling or referencing time
- Action items: include owner + due date when relevant

## Writing preferences

- Emoji: avoid
- Tone: direct
- "No-go" phrases: "circle back", "synergy", "leverage", "touch base", "at the end of the day"

## File conventions (when Pal writes files)

- Meeting notes path: `context/meetings/`
- Meeting notes filename: `YYYY-MM-DD - meeting - topic.md`
- Weekly review path: `context/meetings/`
- Weekly review filename: `YYYY-MM-DD - weekly-review.md`
- Project docs path: `context/projects/`
- Project doc filename: `project - <name>.md`

## Scheduled tasks

Pal runs these automatically — no prompting required:

| Task | Schedule | What it does |
|------|----------|-------------|
| Daily briefing | 8 AM weekdays | Calendar, emails, priorities |
| Inbox digest | 12 PM weekdays | Morning email summary, flag responses |
| Weekly review | 5 PM Friday | Fill weekly-review template, save to meetings/ |
| Context refresh | 8 AM daily | Re-index context files via update_knowledge |
| Learning summary | 10 AM Monday | Summarize patterns from pal_learnings |

If a scheduled task produces a file, follow the file conventions above.

## Governance

- Always confirm before: creating events with external attendees, drafting external emails
- Never do: send emails directly, delete files, drop database tables without confirmation
