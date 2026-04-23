-- 1. User
CREATE TABLE "User"
(
    user_id INT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    nickname VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP
);

-- 2. Workspace
CREATE TABLE Workspace
(
    workspace_id INT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    creator_user_id INT,
    created_at TIMESTAMP,
    FOREIGN KEY (creator_user_id) REFERENCES "User"(user_id)
);

-- 3. Workspace Admin
CREATE TABLE WorkspaceAdmin
(
    workspace_id INT,
    user_id INT,
    assigned_at TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id),
    FOREIGN KEY (workspace_id) REFERENCES Workspace(workspace_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id)
);

-- 4. Workspace Membership
CREATE TABLE WorkspaceMembership
(
    workspace_id INT,
    user_id INT,
    joined_at TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id),
    FOREIGN KEY (workspace_id) REFERENCES Workspace(workspace_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id)
);

-- 5. Workspace Invitation
CREATE TABLE WorkspaceInvitation
(
    invitation_id INT PRIMARY KEY,
    workspace_id INT,
    invited_user_id INT,
    invited_by_user_id INT,
    invited_at TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('pending', 'accepted', 'rejected')),
    FOREIGN KEY (workspace_id) REFERENCES Workspace(workspace_id),
    FOREIGN KEY (invited_user_id) REFERENCES "User"(user_id),
    FOREIGN KEY (invited_by_user_id) REFERENCES "User"(user_id)
);

-- 6. Channel
CREATE TABLE Channel
(
    channel_id INT PRIMARY KEY,
    workspace_id INT,
    name VARCHAR(100),
    channel_type VARCHAR(20) CHECK (channel_type IN ('public', 'private')),
    creator_user_id INT,
    created_at TIMESTAMP,
    FOREIGN KEY (workspace_id) REFERENCES Workspace(workspace_id),
    FOREIGN KEY (creator_user_id) REFERENCES "User"(user_id)
);

-- 7. Channel Membership
CREATE TABLE ChannelMembership
(
    channel_id INT,
    user_id INT,
    joined_at TIMESTAMP,
    PRIMARY KEY (channel_id, user_id),
    FOREIGN KEY (channel_id) REFERENCES Channel(channel_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id)
);

-- 8. Channel Invitation
CREATE TABLE ChannelInvitation
(
    invitation_id INT PRIMARY KEY,
    channel_id INT,
    invited_user_id INT,
    invited_by_user_id INT,
    invited_at TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('pending', 'accepted', 'rejected')),
    FOREIGN KEY (channel_id) REFERENCES Channel(channel_id),
    FOREIGN KEY (invited_user_id) REFERENCES "User"(user_id),
    FOREIGN KEY (invited_by_user_id) REFERENCES "User"(user_id)
);

-- 9. Direct Channel Participant
CREATE TABLE DirectChannelParticipant
(
    channel_id INT,
    user_id INT,
    PRIMARY KEY (channel_id, user_id),
    FOREIGN KEY (channel_id) REFERENCES Channel(channel_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id)
);

-- 10. Message
CREATE TABLE Message
(
    message_id INT PRIMARY KEY,
    channel_id INT,
    sender_user_id INT,
    body TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES Channel(channel_id),
    FOREIGN KEY (sender_user_id) REFERENCES "User"(user_id)
);