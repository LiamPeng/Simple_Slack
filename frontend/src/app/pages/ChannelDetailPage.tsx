import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { AppLayout } from '../components/AppLayout';
import { channelsAPI, ChannelDetail, ChannelMember, Message } from '../api/channels';
import { workspacesAPI } from '../api/workspaces';
import { getApiErrorMessage } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Send, Hash, Lock, Users, UserPlus } from 'lucide-react';

export function ChannelDetailPage() {
  const { channelId } = useParams<{ channelId: string }>();
  const { user } = useAuth();
  const [channel, setChannel] = useState<ChannelDetail | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInviteToChannel, setShowInviteToChannel] = useState(false);
  const [showMembersModal, setShowMembersModal] = useState(false);
  const [messageContent, setMessageContent] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadChannelData();
  }, [channelId, user?.id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChannelData = async () => {
    setLoading(true);
    try {
      const channelData = await channelsAPI.getChannelDetail(Number(channelId));
      setChannel(channelData);
      setMessages(channelData.messages);
    } catch (error) {
      console.error('Error loading channel:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!messageContent.trim()) return;

    setSendingMessage(true);
    try {
      const newMessage = await channelsAPI.createMessage(Number(channelId), {
        body: messageContent,
      });
      setMessages([...messages, newMessage]);
      setMessageContent('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setSendingMessage(false);
    }
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </AppLayout>
    );
  }

  if (!channel) {
    return (
      <AppLayout>
        <div className="text-center py-12">
          <p className="text-gray-600">Channel not found</p>
        </div>
      </AppLayout>
    );
  }

  const displayName = channel.channel_type === 'direct' && channel.other_user
    ? channel.other_user.username
    : channel.name;

  const channelTypeLabel =
    channel.channel_type === 'public' ? 'Public channel' :
    channel.channel_type === 'private' ? 'Private channel' :
    'Direct message';

  const isChannelCreator = user?.id === channel.creator;

  return (
    <AppLayout>
      <div className="flex flex-col h-full">
        {/* Channel Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-3 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {channel.channel_type === 'public' ? (
                <Hash className="h-5 w-5 text-gray-600" />
              ) : channel.channel_type === 'direct' ? (
                <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white text-sm font-semibold">
                  {displayName.charAt(0).toUpperCase()}
                </div>
              ) : (
                <Lock className="h-5 w-5 text-gray-600" />
              )}
              <div>
                <h1 className="text-lg font-bold text-gray-900">{displayName}</h1>
                <p className="text-xs text-gray-500">
                  {channel.channel_type === 'direct' && channel.other_user ? (
                    <>
                      {channelTypeLabel} • {channel.other_user.email}
                    </>
                  ) : channel.channel_type === 'private' ? (
                    <>
                      {channelTypeLabel} • {channel.members.length} member
                      {channel.members.length !== 1 ? 's' : ''}
                    </>
                  ) : (
                    channelTypeLabel
                  )}
                </p>
              </div>
            </div>

            {channel.channel_type === 'private' && (
              <div className="flex items-center gap-2">
                {isChannelCreator && (
                  <button
                    type="button"
                    onClick={() => setShowInviteToChannel(true)}
                    className="flex items-center space-x-2 text-sm px-3 py-1.5 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50"
                  >
                    <UserPlus className="h-4 w-4" />
                    <span>Invite</span>
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => setShowMembersModal(true)}
                  className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 px-2 py-1 rounded-md hover:bg-gray-100"
                >
                  <Users className="h-4 w-4" />
                  <span>Members</span>
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 bg-gray-50">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No messages yet. Start the conversation!</p>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {messages.map((message) => {
                const isOwn = message.sender.id === user?.id;
                const timeStr = new Date(message.created_at).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                });

                return (
                  <div
                    key={message.id}
                    className={`flex w-full ${isOwn ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`flex max-w-[min(85%,28rem)] items-end gap-2 ${isOwn ? 'flex-row-reverse' : 'flex-row'}`}
                    >
                      {!isOwn && (
                        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
                          {message.sender.username.charAt(0).toUpperCase()}
                        </div>
                      )}
                      <div className={`min-w-0 flex flex-col ${isOwn ? 'items-end' : 'items-start'}`}>
                        {!isOwn && (
                          <div className="flex items-baseline gap-2 mb-0.5 px-1">
                            <span className="font-semibold text-xs text-gray-700">{message.sender.username}</span>
                            <span className="text-[10px] text-gray-400">{timeStr}</span>
                          </div>
                        )}
                        <div
                          className={`rounded-2xl px-3.5 py-2 shadow-sm whitespace-pre-wrap break-words text-sm ${
                            isOwn
                              ? 'rounded-br-md bg-blue-600 text-white'
                              : 'rounded-bl-md bg-white text-gray-900 border border-gray-100'
                          }`}
                        >
                          <p>{message.body}</p>
                          {isOwn && (
                            <p className="text-[10px] text-blue-100 mt-1 text-right opacity-90">{timeStr}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Message Input */}
        <div className="border-t border-gray-200 bg-white px-6 py-4 flex-shrink-0">
          <form onSubmit={handleSendMessage}>
            <div className="flex items-end space-x-3">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={messageContent}
                  onChange={(e) => setMessageContent(e.target.value)}
                  placeholder={
                    channel.channel_type === 'direct'
                      ? `Message ${displayName}`
                      : `Message #${channel.name}`
                  }
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <button
                type="submit"
                disabled={!messageContent.trim() || sendingMessage}
                className="px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </form>
        </div>
      </div>

      {showInviteToChannel && channel && channel.channel_type === 'private' && (
        <InviteToPrivateChannelModal
          workspaceId={channel.workspace}
          channelId={channel.id}
          channelName={channel.name}
          onClose={() => setShowInviteToChannel(false)}
        />
      )}

      {showMembersModal && channel && channel.channel_type === 'private' && (
        <PrivateChannelMembersModal
          channelName={channel.name}
          members={channel.members}
          onClose={() => setShowMembersModal(false)}
        />
      )}
    </AppLayout>
  );
}

function PrivateChannelMembersModal({
  channelName,
  members,
  onClose,
}: {
  channelName: string;
  members: ChannelMember[];
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
      role="presentation"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg max-w-md w-full max-h-[min(70vh,28rem)] shadow-xl flex flex-col"
        role="dialog"
        aria-labelledby="members-modal-title"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between flex-shrink-0">
          <h2 id="members-modal-title" className="text-lg font-bold text-gray-900">
            Members of #{channelName}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="text-sm text-gray-500 hover:text-gray-800 px-2 py-1 rounded-md hover:bg-gray-100"
          >
            Close
          </button>
        </div>
        <ul className="overflow-y-auto px-2 py-2">
          {members.length === 0 ? (
            <li className="px-4 py-6 text-sm text-gray-500 text-center">No members listed.</li>
          ) : (
            members.map((m) => (
              <li
                key={m.id}
                className="flex items-center gap-3 px-4 py-2.5 rounded-md hover:bg-gray-50"
              >
                <div className="w-9 h-9 rounded-full bg-blue-600 flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
                  {m.username.charAt(0).toUpperCase()}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-medium text-gray-900 truncate">{m.username}</p>
                  <p className="text-xs text-gray-500">Joined {new Date(m.joined_at).toLocaleDateString()}</p>
                </div>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}

function InviteToPrivateChannelModal({
  workspaceId,
  channelId,
  channelName,
  onClose,
}: {
  workspaceId: number;
  channelId: number;
  channelName: string;
  onClose: () => void;
}) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);
    try {
      await workspacesAPI.inviteUser(workspaceId, email.trim(), channelId);
      setSuccess(true);
      setEmail('');
    } catch (err: unknown) {
      setError(getApiErrorMessage(err, 'Failed to send invitation'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
        <h2 className="text-xl font-bold text-gray-900 mb-1">Invite to private channel</h2>
        <p className="text-sm text-gray-600 mb-4">
          Adds them to this workspace as a member and to <span className="font-medium">#{channelName}</span> when they
          accept. Only you (the channel creator) can send these invitations.
        </p>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4 text-sm">{error}</div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded mb-4 text-sm">
            Invitation sent.
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <label htmlFor="invite-channel-email" className="block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            id="invite-channel-email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="colleague@example.com"
            className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
          <div className="mt-6 flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Close
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Sending…' : 'Send invitation'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
