# Milestone: Invitation Log

---

## As an OWNER or ADMIN I want to audit the invitation log so that I can track whats happening with invites.

**Functional requirements:**
- When an action is taken on an invite, the invite is logged. (see Invite log)
- Owners and admins have permission to view the invite log.
- Members do not have permission to view the invite log.
- The invite log should display the following information:
  - Invitee email hash (sha256)
  - timestamp
  - message
  - organization

**Non-functional requirements:**
- The invite log is available to owners and admins only within the dashboard.
- OWNERs and ADMINs have permission to view the invite log.
- Members do not have permission to view the invite log.

**Error handling:**
- If there is an error sending the email invite, then log it.

---
