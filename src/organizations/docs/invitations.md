# Milestone: Invitations (CRUD)

---

## Global Requirements and Error Handling

**Functional requirements:**
- When an action is taken on an invite, the invite is logged. (see Invite log)

**Non-functional requirements:**
- TBD

**Error Handling:**
- If the user is not logged in, then redirect to the login page.
- If the user is not a member of the organization, then return an error message.
- If the organization does not exist, then return an error message.
- If the organization is deleted, then return an error message.
- If the organization is soft-deleted, then return an error message.
- If the organization is soft-deleted, then return an error message.
- If the invite does not exist, then return an error message.

---

## As an OWNER or ADMIN I want to CREATE invitations so that users can join the organization.

**Functional requirements:**
- Admins and owners have permission to invite users.
- Users who are already members of the organization may not be invited.
- Members DO NOT have permission to invite other members.
- Invitations do not expire.
- Users may have multiple pending invitations from different organizations.
- Users can be re-invited to an organization if they decline the invitation.
- There should only ever be one invitation per user per organization

**Error handling:**
- Attempting to invite a user who is already a member of the organization
  should return an error message.
- Attempting to invite a user who has already been invited should return an
  error message.
- Org MEMBERs attempting to invite other members should return an error message.

---

## As an OWNER or ADMIN I want to REVOKE invitations in case of error or change of plans.

**Functional requirements:**
- Admins and owners have permission to revoke invitations.
- Members do not have permission to revoke invitations.
- Revoking an invitation should remove the invite record from the database.
- Revoking an invitation should log the action in the invite log.

**Error handling:**
- MEMBERs attempting to revoke an invitation should return an error message.
- If logged in as one user and attempting to revoke an invite on behalf of
  another user, then return an error message.

---

## As a USER I want to ACCEPT an invitation so that I can join the organization.

**Functional requirements:**
- Users must accept the invitation to join the organization.
- Users may only accept an invitation once.
- Users may not accept an invitation if they have already declined it.
- Other users may not accept an invitation on behalf of another user.
- Accepting an invitation should create a log entry in the invite log.
- Invites are removed completely once accepted.
- If the user is already a user of the system, then the user should be
  automatically added to the organization.
- If the user is not already a user of the system, then the user should be
  prompted to create an account.

**Error handling:**
- If logged in as one user and attempting to accept/decline an invite on
  behalf of another user, then return an error message.
- If the invite does not exist, then return an error message.

---

## As a USER I want to DECLINE an invitation so that I do not join the organization.

**Functional requirements:**
- Invitations may be declined by the invitee.
- Users may only decline an invitation once.
- Users may not decline an invitation if they are already a member of the
  inviting organization.
- Declining an invitation should remove the invite record from the database.
- Declining an invitation should log the action in the invite log.

**Error handling:**

---

## As an OWNER or ADMIN I want to SEND reminders to invitees so that they join the organization.

**Functional requirements:**
- Admins and owners have permission to send reminders to invitees.
- Members do not have permission to send reminders to invitees.
- Reminders may be sent to invitees who have not yet accepted the invitation.
- Sending a reminder should log the action in the invite log.

**Error handling:**
- MEMBERs attempting to send reminders to invitees should return an error message.
- If there is an error sending the reminder, then log it.
- If the invite does not exist, then return an error message.

---

## As an OWNER or ADMIN I want to VIEW pending invitations so that I can see who has not yet accepted.

**Functional requirements:**
- Owners and admins have permission to view the pending invites.
- Members do not have permission to view the pending invites.

**Error handling:**
- MEMBERs attempting to view the pending invites should return an error message.

---

## As a USER I want to receive my organization invitation via EMAIL so that I can join the organization.

**Functional requirements:**
- Users should receive an email invitation to join the organization.
- The email should contain a link to accept the invitation.
- The email should contain a link to decline the invitation.
- The email should contain a link to view the organization details.
- Sending an email should create a log entry in the invite log.

**Non-functional requirements:**
- The email should be sent immediately after the invitation is created.
- The email should be sent from a no-reply email address.
- The email should be sent in plain text format.
- The email should arrive within 5 minutes of the invitation being created.
- Emails should be sent using a third-party email service.
- The email should contain the organization name and a brief description of the
  organization.
- The email should contain the name of the person who invited the user.

**Error handling:**
- If there is an error sending the email invite, then log it.
