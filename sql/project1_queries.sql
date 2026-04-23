-- create a new user account
INSERT INTO "User"
VALUES
    (6, 'ben@example.com', 'ben', 'benny', 'hash6', '2026-04-22 09:00:00');

-- create a new public channel in workspace1 by an admin
INSERT INTO Channel
    (channel_id, workspace_id, name, channel_type, creator_user_id, created_at)
SELECT 5, 1, 'linear-algebra', 'public', 2, '2026-04-10 12:00:00'
WHERE EXISTS (
    SELECT 1
FROM WorkspaceAdmin
WHERE workspace_id = 1
    AND user_id IN (1, 2)
);

-- admin in each workspace
SELECT w.workspace_id, w.name, wa.user_id
FROM workspace w
    JOIN WorkspaceAdmin wa ON w.workspace_id = wa.workspace_id;

-- # of users invited not yet accepted for more than 5 days in public channels in workspace1
SELECT c.channel_id, COUNT(ci.invited_user_id) AS pending_invites
FROM ChannelInvitation ci
    JOIN Channel c ON ci.channel_id = c.channel_id
    JOIN Workspace w ON c.workspace_id = w.workspace_id
WHERE w.workspace_id = 1
    AND ci.status = 'pending'
    AND c.channel_type = 'public'
    AND ci.invited_at < NOW() - INTERVAL
'5 days'
GROUP BY c.channel_id;

-- messages in chronological order in channel 1
SELECT m.channel_id, m.created_at, m.message_id, m.body
FROM message m
WHERE m.channel_id = 1
ORDER BY m.created_at ASC;

-- messages sent by user2
SELECT m.sender_user_id, m.body, m.channel_id
FROM message m
WHERE m.sender_user_id = 2;

-- user1 with keyword “perpendicular” accessible
SELECT cm.user_id, m.body, m.channel_id, wm.workspace_id
FROM message m
    JOIN Channel c ON m.channel_id = c.channel_id
    JOIN ChannelMembership cm ON m.channel_id = cm.channel_id
    JOIN WorkspaceMembership wm ON wm.workspace_id = c.workspace_id
WHERE cm.user_id = 1 AND wm.user_id = 1
    AND m.body LIKE '%perpendicular%';