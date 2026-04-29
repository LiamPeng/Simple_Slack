import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { AppLayout } from '../components/AppLayout';
import { channelsAPI, ChannelDetail, Message } from '../api/channels';
import { useAuth } from '../context/AuthContext';
import { Send, Hash, Lock, Users } from 'lucide-react';

export function ChannelDetailPage() {
  const { channelId } = useParams<{ channelId: string }>();
  const { user } = useAuth();
  const [channel, setChannel] = useState<ChannelDetail | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [messageContent, setMessageContent] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadChannelData();
  }, [channelId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChannelData = async () => {
    try {
      const [channelData, messagesData] = await Promise.all([
        channelsAPI.getChannelDetail(Number(channelId)),
        channelsAPI.getMessages(Number(channelId)),
      ]);
      setChannel(channelData);
      setMessages(messagesData);
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
        content: messageContent,
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
                  {channelTypeLabel}
                  {channel.channel_type === 'direct' && channel.other_user && (
                    <> • {channel.other_user.email}</>
                  )}
                  {channel.channel_type !== 'direct' && (
                    <> • {channel.members.length} member{channel.members.length !== 1 ? 's' : ''}</>
                  )}
                </p>
              </div>
            </div>

            {channel.channel_type !== 'direct' && (
              <button className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900">
                <Users className="h-4 w-4" />
                <span>Members</span>
              </button>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4 bg-white">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">No messages yet. Start the conversation!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => {
                const isOwnMessage = message.sender.id === user?.id;
                return (
                  <div key={message.id} className="flex items-start space-x-3">
                    <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
                      {message.sender.username.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-baseline space-x-2 mb-1">
                        <span className="font-semibold text-sm text-gray-900">
                          {message.sender.username}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                      <p className="text-sm text-gray-800 whitespace-pre-wrap break-words">
                        {message.content}
                      </p>
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
    </AppLayout>
  );
}
