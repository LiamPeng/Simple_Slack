-- 1. User
CREATE TABLE User
(
    user_id INT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    nickname VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Workspace
CREATE TABLE Workspace
(
    workspace_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    creator_user_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_user_id) REFERENCES "User"(user_id)
);

-- 3. Workspace Admin
CREATE TABLE WorkspaceAdmin
(
    workspace_id INT NOT NULL,
    user_id INT NOT NULL,
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id),
    FOREIGN KEY (workspace_id) REFERENCES Workspace(workspace_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id)
);

-- 4. Workspace Membership
CREATE TABLE WorkspaceMembership
(
    workspace_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (workspace_id, user_id),
    FOREIGN KEY (workspace_id) REFERENCES Workspace(workspace_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id)
);

-- 5. Workspace Invitation
CREATE TABLE WorkspaceInvitation
(
    invitation_id INT PRIMARY KEY,
    workspace_id INT NOT NULL,
    invited_user_id INT NOT NULL,
    invited_by_user_id INT NOT NULL,
    invited_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'accepted', 'declined')),
    FOREIGN KEY (workspace_id) REFERENCES Workspace(workspace_id),
    FOREIGN KEY (invited_user_id) REFERENCES "User"(user_id),
    FOREIGN KEY (invited_by_user_id) REFERENCES "User"(user_id)
);

-- 6. Channel
CREATE TABLE Channel
(
    channel_id INT PRIMARY KEY,
    workspace_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    channel_type VARCHAR(20) NOT NULL CHECK (channel_type IN ('public', 'private','direct')),
    creator_user_id INT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (workspace_id, name),
    FOREIGN KEY (workspace_id) REFERENCES Workspace(workspace_id),
    FOREIGN KEY (creator_user_id) REFERENCES "User"(user_id)
);

-- 7. Channel Membership
CREATE TABLE ChannelMembership
(
    channel_id INT NOT NULL,
    user_id INT NOT NULL,
    joined_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (channel_id, user_id),
    FOREIGN KEY (channel_id) REFERENCES Channel(channel_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id)
);

-- 8. Channel Invitation
CREATE TABLE ChannelInvitation
(
    invitation_id INT PRIMARY KEY,
    channel_id INT NOT NULL,
    invited_user_id INT NOT NULL,
    invited_by_user_id INT NOT NULL,
    invited_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'accepted', 'declined')),
    FOREIGN KEY (channel_id) REFERENCES Channel(channel_id),
    FOREIGN KEY (invited_user_id) REFERENCES "User"(user_id),
    FOREIGN KEY (invited_by_user_id) REFERENCES "User"(user_id)
);

-- 9. Direct Channel Participant
CREATE TABLE DirectChannelParticipant
(
    channel_id INT NOT NULL,
    user_id INT NOT NULL,
    PRIMARY KEY (channel_id, user_id),
    FOREIGN KEY (channel_id) REFERENCES Channel(channel_id),
    FOREIGN KEY (user_id) REFERENCES "User"(user_id)
);

-- 10. Message
CREATE TABLE Message
(
    message_id INT PRIMARY KEY,
    channel_id INT NOT NULL,
    sender_user_id INT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (channel_id) REFERENCES Channel(channel_id),
    FOREIGN KEY (sender_user_id) REFERENCES "User"(user_id)
);