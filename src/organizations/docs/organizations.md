# Milestone: Organization CRUD

## As a USER, I want to CREATE an organization so that I can collaborate with my team members on projects.

**Functional requirements:**
- An organization must have a name.
- The organization name must be unique.
- The organization name must be between 3 and 50 characters.
- The organization description is optional.
- The organization owner must be a member of the organization.
- Upon creation of the organization, the user is automatically added as the
  owner of the organization.
- Any registered user may create an organization.
- Names cannot conflict with names in the org name history table.

**Non-functional requirements:**
- The organization creation form should be accessible from the user dashboard.
- It should take less than 3 seconds to create the organization after the user
  clicks the "Create" button.
- No offensive names should be allowed for the organization name.
- Names cannot conflict with reserved names (e.g. "admin", "root", "superuser")

**Error Handling:**
- If the organization name is not unique, then return an error message.
- If the organization name is less than 3 characters, then return an error
  message.
- If the organization name is greater than 50 characters, then return an error
  message.
- If the user is not logged in, then redirect to the login page.
- If the user is not a member of the organization, then return an error message.

## As an organization member, I want to READ (see details) an organization so that I can view the organization details.

**Functional requirements:**
- The organization details page should display the organization name.
- The organization details page should display the organization description.
- The organization details page should display the organizations members and
  their roles.
- The details page is only available to ACTIVE members of the organization
- The details page is not available to NON-members of the organization
- The details page is not available to INACTIVE members of the organization
- The details page is not available to PENDING or INVITED members of the
  organization (until they accept the invite)
- Soft-deleted organizations may not be viewed.

**Non-functional requirements:**
- The organization details page should be accessible from the user dashboard.
- It should take less than 3 seconds to load the organization details page.
- The organization details should work on desktop or laptop displays

**Error Handling:**
- If the user is not logged in, then redirect to the login page.
- If the user is not a member of the organization, then return an error message.
- If the user is an INACTIVE member of the organization, then return an error
  message.
- If the user is a PENDING or INVITED member of the organization, then return an
  error message.
- If the organization does not exist, then return an error message.
- If the organization is deleted, then return an error message.


## As an OWNER or ADMIN, I want to UPDATE an organization so that I can change the organization settings.

**Functional requirements:**
- Owners and admins have permission to update the organization settings.
- Members do not have permission to update the organization settings.
- Non-members do not have permission to update the organization settings.
- Soft-deleted organizations may not be updated.

**Non-functional requirements:**
- The organization settings page should be accessible from the user dashboard.
- It should take less than 3 seconds to update the organization settings after
  the user clicks the "Update" button.
- The organization settings should work on desktop or laptop displays
- The organization settings page should display the organization name.

**Error Handling:**
- If the user is not logged in, then redirect to the login page.
- If the user is not an owner or admin of the organization, then return an error
  message.
- If the user role is MEMBER of the organization, then return an error message.
- If the organization does not exist, then return an error message.
- If the organization is deleted, then return an error message.

## As an OWNER, I want to DELETE an organization so that I can remove the organization from the app.

**Functional requirements:**
- Only owners may delete the organization.
- ADMINs and MEMBERS do not have permission to delete the organization.
- Non-members do not have permission to delete the organization.
- When an organization is deleted, all assets and resources associated with the
  organization are also deleted.
- When deleted, the organization name is copied to the organization name
  history table.
- When an OWNER deletes the org, it is soft-deleted by setting the is_deleted
  flag to True.
- The OWNER must confirm deletion by typing the organization name in a text
  field before submitting the deletion request.

**Non-functional requirements:**
- The organization deletion page should be accessible from the user dashboard.
- It should take less than 3 seconds to delete the organization after the user
  clicks the "Delete" button.
- The organization deletion should work on desktop or laptop displays

**Error Handling:**
- If the user is not logged in, then redirect to the login page.
- If the user is not an owner of the organization, then return an error message.

---
