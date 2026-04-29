Project #2 Outline: Django Web Application for Workspace Messaging System
React Frontend + Django API Backend + PostgreSQL

1. Project Overview

This project will implement a web-based workspace messaging system based on the database design from Project #1. The application allows users to register, log in, create workspaces, create channels, invite other users, post messages, browse accessible content, and search messages.

The system will use React as the frontend, Django as the backend API server, and PostgreSQL as the relational database. Django models will redefine the database schema based on Project #1, and Django migrations will generate the PostgreSQL tables. The React frontend will communicate with the Django backend through HTTP API requests.

The main goal is to build a functional and secure web application that demonstrates the database schema, relationships, constraints, access control, SQL injection prevention, XSS prevention, and transaction handling.

2. Technology Stack

Frontend:
- React
- Tailwind CSS or regular CSS
- JavaScript
- Fetch API or Axios for API requests

Backend:
- Django
- Django ORM
- Django session authentication or token-based authentication
- Django transaction management

Database:
- PostgreSQL

Security:
- Django ORM for SQL injection prevention
- React text rendering for XSS prevention
- CSRF protection for unsafe requests if using session authentication
- Password hashing through Django authentication system
- Access control checks in backend views

3. System Architecture

The system architecture is:

React Frontend
    |
    | HTTP requests using fetch or axios
    v
Django Backend API
    |
    | Django ORM queries and transactions
    v
PostgreSQL Database

React is responsible for rendering the user interface and sending user actions to the backend. Django is responsible for authentication, authorization, business logic, database operations, and returning JSON responses. PostgreSQL stores all persistent data.

4. Main Database Entities

4.1 User Module

The user module represents registered users of the system.

Recommended implementation:
- Use Django's built-in User model if possible.

Main responsibilities:
- Register new users
- Log in users
- Log out users
- Track the currently authenticated user
- Associate users with workspaces, channels, messages, and invitations

Important constraints:
- Username or email should be unique.
- Passwords should never be stored as plain text.
- Passwords should be hashed using Django's built-in authentication system.

4.2 Workspace Module

A workspace is a shared area that contains channels and members.

Possible model:
- Workspace

Main attributes:
- workspace_id
- name
- description
- creator
- created_at

Main functions:
- Create a new workspace
- List workspaces that the current user belongs to
- View workspace details
- Show channels inside a workspace
- Show members inside a workspace

Important constraints:
- Workspace name cannot be empty.
- Workspace creator must be a valid user.
- The creator should automatically become an admin member of the workspace.

Transaction requirement:
- Creating a workspace and creating the creator's WorkspaceMembership should happen in one transaction.

4.3 Workspace Membership Module

WorkspaceMembership represents the relationship between users and workspaces.

Possible model:
- WorkspaceMembership

Main attributes:
- membership_id
- workspace
- user
- role
- joined_at

Possible roles:
- admin
- member

Main functions:
- Check whether a user belongs to a workspace
- Check whether a user is an admin of a workspace
- List workspace members
- Prevent non-members from accessing workspace content

Important constraints:
- A user should not have duplicate membership in the same workspace.
- Role should be limited to valid choices.

Useful database constraint:
- UNIQUE(workspace, user)

4.4 Channel Module

A channel belongs to a workspace and contains messages.

Possible model:
- Channel

Main attributes:
- channel_id
- workspace
- name
- channel_type
- creator
- created_at

Possible channel types:
- public
- private
- direct

Main functions:
- Create a channel inside a workspace
- List channels in a workspace
- View channel details
- Show messages in a channel

Important constraints:
- Channel name cannot be empty.
- Channel name should be unique within the same workspace.
- Channel must belong to a valid workspace.
- Creator must be a member of the workspace.
- Channel type should be limited to valid choices.

Useful database constraint:
- UNIQUE(workspace, name)

Transaction requirement:
- Creating a channel and adding the creator to ChannelMembership should happen in one transaction.

4.5 Channel Membership Module

ChannelMembership represents which users can access which channels.

Possible model:
- ChannelMembership

Main attributes:
- channel_membership_id
- channel
- user
- joined_at

Main functions:
- Check whether a user can view a channel
- List channel members
- Add users to private or direct channels
- Prevent unauthorized users from reading or posting messages

Important constraints:
- A user should not have duplicate membership in the same channel.
- A user should belong to the workspace before joining a channel.

Useful database constraint:
- UNIQUE(channel, user)

Special assumption:
- For direct channels, each direct channel should have exactly two channel members.
- This rule may be enforced at the application level for simplicity.

4.6 Message Module

A message is posted by a user inside a channel.

Possible model:
- Message

Main attributes:
- message_id
- channel
- sender
- content
- created_at
- updated_at

Main functions:
- Post a message
- View messages in a channel
- Search messages
- Optionally edit or delete own messages

Important constraints:
- Message content cannot be empty.
- Sender must be a channel member or have permission to access the channel.
- Message must belong to a valid channel.

Security requirement:
- Message content must be displayed safely on the frontend to prevent XSS.

4.7 Invitation Module

An invitation allows a user to invite another user to a workspace or channel.

Possible model:
- Invitation

Main attributes:
- invitation_id
- inviter
- invitee
- workspace
- channel
- status
- created_at
- responded_at

Possible statuses:
- pending
- accepted
- rejected

Main functions:
- Invite a user to a workspace
- Invite a user to a private channel
- View pending invitations
- Accept an invitation
- Reject an invitation

Important constraints:
- Inviter must have permission to invite.
- Invitee must be a valid user.
- Status should be limited to valid choices.
- Duplicate pending invitations should be prevented.

Transaction requirement:
- Accepting an invitation and creating the corresponding membership should happen in one transaction.

5. Backend API Modules

The Django backend will expose API endpoints that return JSON responses to the React frontend.

5.1 Authentication API

Endpoints:
- POST /api/register/
- POST /api/login/
- POST /api/logout/
- GET /api/me/

Responsibilities:
- Register a new user
- Authenticate login credentials
- Start or end a user session
- Return current user information

5.2 Workspace API

Endpoints:
- GET /api/workspaces/
- POST /api/workspaces/
- GET /api/workspaces/<workspace_id>/

Responsibilities:
- List workspaces accessible to the current user
- Create a new workspace
- Return workspace details, channels, and members

Access control:
- Only workspace members can view workspace details.
- Only authenticated users can create workspaces.

5.3 Channel API

Endpoints:
- POST /api/workspaces/<workspace_id>/channels/
- GET /api/channels/<channel_id>/

Responsibilities:
- Create a channel inside a workspace
- Return channel details
- Return channel members and messages

Access control:
- Only workspace members can create channels.
- Only users with permission can view a channel.

5.4 Message API

Endpoints:
- GET /api/channels/<channel_id>/messages/
- POST /api/channels/<channel_id>/messages/

Responsibilities:
- Return messages in a channel
- Create a new message in a channel

Access control:
- A user can only view or post messages in channels they can access.

5.5 Invitation API

Endpoints:
- GET /api/invitations/
- POST /api/workspaces/<workspace_id>/invite/
- POST /api/invitations/<invitation_id>/accept/
- POST /api/invitations/<invitation_id>/reject/

Responsibilities:
- List pending invitations for the current user
- Send invitations to other users
- Accept invitations
- Reject invitations

Access control:
- Only authorized users, such as workspace admins, can send invitations.
- Only the invited user can accept or reject an invitation.

5.6 Search API

Endpoint:
- GET /api/search/?q=<keyword>

Responsibilities:
- Search messages by keyword
- Return only messages that the current user is allowed to access

Important rule:
- The search API must not search all messages globally without checking permissions.
- It should only search messages in channels accessible to the current user.

6. Frontend React Modules

6.1 React Project Structure

Suggested structure:

src/
  api/
    auth.js
    workspaces.js
    channels.js
    messages.js
    invitations.js
    search.js

  pages/
    LoginPage.jsx
    RegisterPage.jsx
    DashboardPage.jsx
    WorkspaceDetailPage.jsx
    ChannelDetailPage.jsx
    InvitationsPage.jsx
    SearchPage.jsx

  components/
    Navbar.jsx
    Sidebar.jsx
    WorkspaceCard.jsx
    ChannelList.jsx
    MessageList.jsx
    MessageInput.jsx
    InvitationCard.jsx
    SearchBar.jsx

  App.jsx
  main.jsx

6.2 Login Page

Main functions:
- User enters username/email and password.
- Frontend sends login request to Django backend.
- If login succeeds, user is redirected to dashboard.
- If login fails, error message is displayed.

API used:
- POST /api/login/

6.3 Register Page

Main functions:
- User enters username, email, password, and password confirmation.
- Frontend sends register request to backend.
- If registration succeeds, user is redirected to login or dashboard.

API used:
- POST /api/register/

6.4 Dashboard Page

Main functions:
- Show current user information.
- Show list of workspaces the user belongs to.
- Show pending invitations.
- Provide button to create workspace.
- Provide search bar or link to search page.

APIs used:
- GET /api/me/
- GET /api/workspaces/
- GET /api/invitations/

6.5 Workspace Detail Page

Main functions:
- Show workspace name and description.
- Show channels in the workspace.
- Show workspace members.
- Provide button to create channel.
- Provide invitation form or invite button.

API used:
- GET /api/workspaces/<workspace_id>/

6.6 Channel Detail Page

Main functions:
- Show channel name and type.
- Show message list.
- Show message input box.
- Allow user to send a message.
- Show channel members.

APIs used:
- GET /api/channels/<channel_id>/
- GET /api/channels/<channel_id>/messages/
- POST /api/channels/<channel_id>/messages/

6.7 Invitations Page

Main functions:
- Show pending invitations.
- Allow user to accept or reject invitations.

APIs used:
- GET /api/invitations/
- POST /api/invitations/<invitation_id>/accept/
- POST /api/invitations/<invitation_id>/reject/

6.8 Search Page

Main functions:
- User enters a keyword.
- Frontend calls search API.
- Display matched messages with sender, channel, workspace, and timestamp.

API used:
- GET /api/search/?q=<keyword>

7. Access Control Rules

7.1 Workspace Access

A user can view a workspace only if the user has a WorkspaceMembership record for that workspace.

7.2 Channel Access

Public channel:
- Any workspace member can view it.

Private channel:
- Only users with ChannelMembership can view it.

Direct channel:
- Only the two users in the direct channel can view it.

7.3 Message Access

A user can view, post, or search a message only if the user can access the message's channel.

7.4 Invitation Access

Only the invited user can accept or reject an invitation.
Only authorized users, such as workspace admins, can send invitations.

8. Transaction and Concurrency Plan

The system will use Django's transaction.atomic() for operations that involve multiple related database changes.

8.1 Create Workspace

Steps:
1. Insert a Workspace record.
2. Insert a WorkspaceMembership record for the creator as admin.

These steps should happen in one transaction.

8.2 Create Channel

Steps:
1. Insert a Channel record.
2. Insert a ChannelMembership record for the creator.

These steps should happen in one transaction.

8.3 Accept Invitation

Steps:
1. Update Invitation status to accepted.
2. Insert WorkspaceMembership and/or ChannelMembership.
3. Save responded_at timestamp.

These steps should happen in one transaction.

8.4 Create Direct Channel

Steps:
1. Insert Channel with channel_type = direct.
2. Insert ChannelMembership for the first user.
3. Insert ChannelMembership for the second user.

These steps should happen in one transaction.

9. Security Plan

9.1 SQL Injection Prevention

SQL injection will be prevented mainly by using Django ORM instead of manually concatenating SQL strings.

Safe example:
Message.objects.filter(content__icontains=keyword)

Unsafe example:
cursor.execute(f"SELECT * FROM message WHERE content LIKE '%{keyword}%'")

If raw SQL is needed, parameterized queries will be used.

9.2 XSS Prevention

React normally escapes text content when rendering values inside JSX.

Safe example:
<p>{message.content}</p>

Unsafe example:
<div dangerouslySetInnerHTML={{ __html: message.content }} />

The application will not use dangerouslySetInnerHTML for user-generated content such as message content, usernames, workspace names, or channel names.

9.3 CSRF Protection

If Django session authentication is used, unsafe requests such as POST, PUT, PATCH, and DELETE should include a CSRF token.

Example:
fetch('/api/workspaces/', {
  method: 'POST',
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({ name: 'CS6083 Project' })
});

9.4 Password Security

Passwords will be hashed using Django's built-in authentication system.
Plain-text passwords will never be stored in the database.

9.5 Backend Permission Checks

The backend must check permissions for every important operation.
The frontend should not be trusted as the only access control layer.

10. Demo Flow

A possible demo scenario:

1. Register two users: Alice and Bob.
2. Log in as Alice.
3. Alice creates a workspace called CS6083 Project.
4. Alice creates a public channel called general.
5. Alice posts a message in the general channel.
6. Alice invites Bob to the workspace.
7. Alice logs out.
8. Bob logs in.
9. Bob sees the pending invitation.
10. Bob accepts the invitation.
11. Bob enters the workspace and views the general channel.
12. Bob posts a message.
13. Bob searches for a keyword.
14. The system only returns messages Bob is allowed to access.
15. Show source code for Django models, ORM queries, transaction.atomic(), and React rendering.

11. Required Feature Checklist

Core features:
- User registration
- User login
- User logout
- Current user session or token handling
- Dashboard page
- Create workspace
- List user's workspaces
- View workspace details
- Create channel
- List channels in workspace
- View channel details
- Post message
- View messages
- Invite user
- Accept invitation
- Reject invitation
- Search accessible messages

Security features:
- Use Django ORM instead of string-concatenated SQL
- Use Django password hashing
- Use CSRF protection if using session authentication
- Avoid dangerouslySetInnerHTML in React
- Check backend permissions before returning data
- Prevent unauthorized users from accessing workspace, channel, and message data

Database and transaction features:
- Define Django models with primary keys
- Define foreign keys
- Define unique constraints
- Define role and status choices
- Use transaction.atomic() for multi-step operations
- Prepare sample data for demo

12. Optional Extra Features

Optional features if time allows:
- Edit own messages
- Delete own messages
- Direct message creation
- User profile page
- Search by user, channel, or workspace
- Pagination for messages
- Better UI styling with Tailwind CSS
- Loading states and error messages in React
- Simple notification badges for pending invitations

13. Implementation Priority

Recommended order:

1. Set up Django project.
2. Connect Django to PostgreSQL.
3. Define Django models.
4. Run migrations.
5. Implement authentication APIs.
6. Test APIs with curl, Postman, or browser.
7. Set up React frontend.
8. Build login and register pages.
9. Build dashboard page.
10. Build workspace APIs and pages.
11. Build channel APIs and pages.
12. Build message posting.
13. Build invitation APIs and pages.
14. Build search API and search page.
15. Add access control checks.
16. Add transaction.atomic() to multi-step operations.
17. Add styling and improve UI.
18. Add sample data.
19. Prepare screenshots and logs for writeup.
20. Prepare demo script.

14. Final Recommended Scope

The final project should use:

- React frontend
- Django backend API
- PostgreSQL database
- Django ORM
- Django migrations
- Session authentication or simple token authentication
- transaction.atomic() for multi-step updates
- Backend permission checks
- React rendering without dangerouslySetInnerHTML

The project should focus on correctness, security, and database-centered functionality rather than unnecessary frontend complexity. React will make the interface more modern, but the core grading criteria will still depend on the database design, constraints, transactions, access control, security, documentation, and demo quality.
