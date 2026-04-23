INSERT INTO "User"
VALUES
    (1, 'alice@example.com', 'alice', 'Ali', 'hash1', '2026-01-01 09:00:00'),
    (2, 'bob@example.com', 'bob', 'Bobby', 'hash2', '2026-01-02 07:10:00'),
    (3, 'carol@example.com', 'carol', 'Car', 'hash3', '2026-01-03 21:20:00'),
    (4, 'dave@example.com', 'dave', 'D', 'hash4', '2026-01-04 17:30:00'),
    (5, 'eve@example.com', 'eve', 'Evie', 'hash5', '2026-01-05 20:40:00');

INSERT INTO Workspace
VALUES
    (1, 'Math Club', 'Math discussions', 1, '2026-01-28 16:34:00'),
    (2, 'CS Study Group', 'CS topics', 2, '2026-03-15 11:23:00');

INSERT INTO WorkspaceAdmin
VALUES
    (1, 1, '2026-01-28 16:34:00'),
    (1, 2, '2026-01-29 10:15:00'),
    (2, 2, '2026-03-15 11:23:00');

INSERT INTO WorkspaceMembership
VALUES
    (1, 1, '2026-01-28 16:34:00'),
    (1, 2, '2026-01-29 10:15:00'),
    (1, 3, '2026-01-30 11:38:00'),
    (1, 4, '2026-01-31 18:35:00'),
    (2, 2, '2026-03-15 11:23:00'),
    (2, 3, '2026-03-20 14:25:00'),
    (2, 5, '2026-03-26 19:30:00');

INSERT INTO WorkspaceInvitation
VALUES
    (1, 1, 5, 1, '2026-02-03 09:02:00', 'pending'),
    (2, 1, 3, 2, '2026-02-04 16:30:00', 'accepted'),
    (3, 2, 4, 2, '2026-03-16 11:00:00', 'pending'),
    (4, 2, 1, 2, '2026-03-21 18:22:00', 'rejected');

INSERT INTO Channel
VALUES
    (1, 1, 'general', 'public', 1, '2026-01-28 18:30:00'),
    (2, 1, 'geometry', 'public', 2, '2026-01-30 13:00:00'),
    (3, 1, 'private-chat', 'private', 1, '2026-02-04 14:00:00'),
    (4, 2, 'algorithms', 'public', 2, '2026-03-16 15:00:00');

INSERT INTO ChannelMembership
VALUES
    (1, 1, '2026-01-28 18:30:00'),
    (1, 2, '2026-01-29 12:15:00'),
    (1, 3, '2026-01-30 12:20:00'),
    (2, 1, '2026-01-31 13:10:00'),
    (2, 2, '2026-01-30 13:00:00'),
    (3, 1, '2026-02-04 14:00:00'),
    (4, 2, '2026-03-16 15:00:00'),
    (4, 3, '2026-03-17 15:15:00');

INSERT INTO ChannelInvitation
VALUES
    (1, 1, 4, 1, '2026-02-03 18:30:00', 'pending'),
    (2, 1, 5, 2, '2026-03-08 09:00:00', 'pending'),
    (3, 2, 3, 2, '2026-01-31 15:00:00', 'accepted'),
    (4, 4, 5, 2, '2026-02-04 12:00:00', 'pending'),
    (5, 4, 3, 2, '2026-04-21 12:00:00', 'pending');

INSERT INTO Message
VALUES
    (1, 1, 1, 'Welcome everyone', '2026-01-28 18:35:00'),
    (2, 1, 2, 'This is perpendicular to that line', '2026-01-30 18:30:00'),
    (3, 1, 3, 'Nice to meet you', '2026-01-31 12:40:00'),

    (4, 2, 2, 'Angles are perpendicular here', '2026-01-31 13:00:00'),
    (5, 2, 1, 'Yes, exactly', '2026-02-03 13:35:00'),

    (6, 3, 1, 'Secret discussion', '2026-02-05 14:00:00'),

    (7, 4, 2, 'Dynamic programming today', '2026-03-17 15:30:00'),
    (8, 4, 3, 'I love graphs', '2026-03-18 15:35:00');