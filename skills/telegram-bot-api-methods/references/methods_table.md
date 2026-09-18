# Telegram Bot API Complete Methods Reference (10.3)

**Official Specification Version**: `10.3` (August 24, 2026)
**Total Official Methods**: `185` | **Total Types**: `400`

| # | Method Name | Return Type | Required Parameters | Summary |
| :-: | :--- | :--- | :--- | :--- |
| 1 | `addStickerToSet` | `Boolean` | user_id, name, sticker | Use this method to add a new sticker to a set created by the bot. Emoji sticker sets can h... |
| 2 | `answerCallbackQuery` | `Boolean` | callback_query_id | Use this method to send answers to callback queries sent from inline keyboards. The answer... |
| 3 | `answerChatJoinRequestQuery` | `Boolean` | chat_join_request_query_id, result | Use this method to process a received chat join request query. Returns True on success. |
| 4 | `answerGuestQuery` | `SentGuestMessage` | guest_query_id, result | Use this method to reply to a received guest message. On success, a SentGuestMessage objec... |
| 5 | `answerInlineQuery` | `Boolean` | inline_query_id, results | Use this method to send answers to an inline query. On success, True is returned.No more t... |
| 6 | `answerPreCheckoutQuery` | `Boolean` | pre_checkout_query_id, ok | Once the user has confirmed their payment and shipping details, the Bot API sends the fina... |
| 7 | `answerShippingQuery` | `Boolean` | shipping_query_id, ok | If you sent an invoice requesting a shipping address and the parameter is_flexible was spe... |
| 8 | `answerWebAppQuery` | `SentWebAppMessage` | web_app_query_id, result | Use this method to set the result of an interaction with a Web App and send a correspondin... |
| 9 | `approveChatJoinRequest` | `Boolean` | chat_id, user_id | Use this method to approve a chat join request. The bot must be an administrator in the ch... |
| 10 | `approveSuggestedPost` | `Boolean` | chat_id, message_id | Use this method to approve a suggested post in a direct messages chat. The bot must have t... |
| 11 | `banChatMember` | `Boolean` | chat_id, user_id | Use this method to ban a user in a group, a supergroup or a channel. In the case of superg... |
| 12 | `banChatSenderChat` | `Boolean` | chat_id, sender_chat_id | Use this method to ban a channel chat in a supergroup or a channel. Until the chat is unba... |
| 13 | `close` | `Boolean` | *None* | Use this method to close the bot instance before moving it from one local server to anothe... |
| 14 | `closeForumTopic` | `Boolean` | chat_id, message_thread_id | Use this method to close an open topic in a forum supergroup chat. The bot must be an admi... |
| 15 | `closeGeneralForumTopic` | `Boolean` | chat_id | Use this method to close an open 'General' topic in a forum supergroup chat. The bot must ... |
| 16 | `convertGiftToStars` | `Boolean` | business_connection_id, owned_gift_id | Converts a given regular gift to Telegram Stars. Requires the can_convert_gifts_to_stars b... |
| 17 | `copyMessage` | `MessageId` | chat_id, from_chat_id, message_id | Use this method to copy messages of any kind. Service messages, paid media messages, givea... |
| 18 | `copyMessages` | `Array of MessageId` | chat_id, from_chat_id, message_ids | Use this method to copy messages of any kind. If some of the specified messages can't be f... |
| 19 | `createChatInviteLink` | `ChatInviteLink` | chat_id | Use this method to create an additional invite link for a chat. The bot must be an adminis... |
| 20 | `createChatSubscriptionInviteLink` | `ChatInviteLink` | chat_id, subscription_period, subscription_price | Use this method to create a subscription invite link for a channel chat. The bot must have... |
| 21 | `createForumTopic` | `ForumTopic` | chat_id, name | Use this method to create a topic in a forum supergroup chat or a private chat with a user... |
| 22 | `createInvoiceLink` | `String` | title, description, payload, currency, prices | Use this method to create a link for an invoice. Returns the created invoice link as Strin... |
| 23 | `createNewStickerSet` | `Boolean` | user_id, name, title, stickers | Use this method to create a new sticker set owned by a user. The bot will be able to edit ... |
| 24 | `declineChatJoinRequest` | `Boolean` | chat_id, user_id | Use this method to decline a chat join request. The bot must be an administrator in the ch... |
| 25 | `declineSuggestedPost` | `Boolean` | chat_id, message_id | Use this method to decline a suggested post in a direct messages chat. The bot must have t... |
| 26 | `deleteAllMessageReactions` | `Boolean` | chat_id | Use this method to remove up to 10000 recent reactions in a group or a supergroup chat add... |
| 27 | `deleteBusinessMessages` | `Boolean` | business_connection_id, message_ids | Delete messages on behalf of a business account. Requires the can_delete_sent_messages bus... |
| 28 | `deleteChatPhoto` | `Boolean` | chat_id | Use this method to delete a chat photo. Photos can't be changed for private chats. The bot... |
| 29 | `deleteChatStickerSet` | `Boolean` | chat_id | Use this method to delete a group sticker set from a supergroup. The bot must be an admini... |
| 30 | `deleteEphemeralMessage` | `Boolean` | chat_id, receiver_user_id, ephemeral_message_id | Use this method to delete an ephemeral message. Note that it is not guaranteed that the us... |
| 31 | `deleteForumTopic` | `Boolean` | chat_id, message_thread_id | Use this method to delete a forum topic along with all its messages in a forum supergroup ... |
| 32 | `deleteMessage` | `Boolean` | chat_id, message_id | Use this method to delete a message, including service messages, with the following limita... |
| 33 | `deleteMessageReaction` | `Boolean` | chat_id, message_id | Use this method to remove a reaction from a message in a group or a supergroup chat. The b... |
| 34 | `deleteMessages` | `Boolean` | chat_id, message_ids | Use this method to delete multiple messages simultaneously. If some of the specified messa... |
| 35 | `deleteMyCommands` | `Boolean` | *None* | Use this method to delete the list of the bot's commands for the given scope and user lang... |
| 36 | `deleteStickerFromSet` | `Boolean` | sticker | Use this method to delete a sticker from a set created by the bot. Returns True on success... |
| 37 | `deleteStickerSet` | `Boolean` | name | Use this method to delete a sticker set that was created by the bot. Returns True on succe... |
| 38 | `deleteStory` | `Boolean` | business_connection_id, story_id | Deletes a story previously posted by the bot on behalf of a managed business account. Requ... |
| 39 | `deleteWebhook` | `Boolean` | *None* | Use this method to remove webhook integration if you decide to switch back to getUpdates. ... |
| 40 | `editChatInviteLink` | `ChatInviteLink` | chat_id, invite_link | Use this method to edit a non-primary invite link created by the bot. The bot must be an a... |
| 41 | `editChatSubscriptionInviteLink` | `ChatInviteLink` | chat_id, invite_link | Use this method to edit a subscription invite link created by the bot. The bot must have t... |
| 42 | `editEphemeralMessageCaption` | `Boolean` | chat_id, receiver_user_id, ephemeral_message_id | Use this method to edit the caption of an ephemeral message. Note that it is not guarantee... |
| 43 | `editEphemeralMessageMedia` | `Boolean` | chat_id, receiver_user_id, ephemeral_message_id, media | Use this method to edit the media of an ephemeral message. Note that it is not guaranteed ... |
| 44 | `editEphemeralMessageReplyMarkup` | `Boolean` | chat_id, receiver_user_id, ephemeral_message_id | Use this method to edit only the reply markup of an ephemeral message. Note that it is not... |
| 45 | `editEphemeralMessageText` | `Boolean` | chat_id, receiver_user_id, ephemeral_message_id | Use this method to edit an ephemeral text or rich message. Note that it is not guaranteed ... |
| 46 | `editForumTopic` | `Boolean` | chat_id, message_thread_id | Use this method to edit name and icon of a topic in a forum supergroup chat or a private c... |
| 47 | `editGeneralForumTopic` | `Boolean` | chat_id, name | Use this method to edit the name of the 'General' topic in a forum supergroup chat. The bo... |
| 48 | `editMessageCaption` | `Message, Boolean` | *None* | Use this method to edit captions of messages. On success, if the edited message is not an ... |
| 49 | `editMessageChecklist` | `Message` | business_connection_id, chat_id, message_id, checklist | Use this method to edit a checklist on behalf of a connected business account. On success,... |
| 50 | `editMessageLiveLocation` | `Message, Boolean` | latitude, longitude | Use this method to edit live location messages. A location can be edited until its live_pe... |
| 51 | `editMessageMedia` | `Message, Boolean` | media | Use this method to edit animation, audio, document, live photo, photo, or video messages, ... |
| 52 | `editMessageReplyMarkup` | `Message, Boolean` | *None* | Use this method to edit only the reply markup of messages. On success, if the edited messa... |
| 53 | `editMessageText` | `Message, Boolean` | *None* | Use this method to edit text, rich and game messages. On success, if the edited message is... |
| 54 | `editStory` | `Story` | business_connection_id, story_id, content | Edits a story previously posted by the bot on behalf of a managed business account. Requir... |
| 55 | `editUserStarSubscription` | `Boolean` | user_id, telegram_payment_charge_id, is_canceled | Allows the bot to cancel or re-enable extension of a subscription paid in Telegram Stars. ... |
| 56 | `exportChatInviteLink` | `String` | chat_id | Use this method to generate a new primary invite link for a chat; any previously generated... |
| 57 | `forwardMessage` | `Message` | chat_id, from_chat_id, message_id | Use this method to forward messages of any kind. Service messages and messages with protec... |
| 58 | `forwardMessages` | `Array of MessageId` | chat_id, from_chat_id, message_ids | Use this method to forward multiple messages of any kind. If some of the specified message... |
| 59 | `getAvailableGifts` | `Gifts` | *None* | Returns the list of gifts that can be sent by the bot to users and channel chats. Requires... |
| 60 | `getBusinessAccountGifts` | `OwnedGifts` | business_connection_id | Returns the gifts received and owned by a managed business account. Requires the can_view_... |
| 61 | `getBusinessAccountStarBalance` | `StarAmount` | business_connection_id | Returns the amount of Telegram Stars owned by a managed business account. Requires the can... |
| 62 | `getBusinessConnection` | `BusinessConnection` | business_connection_id | Use this method to get information about the connection of the bot with a business account... |
| 63 | `getChat` | `ChatFullInfo` | chat_id | Use this method to get up-to-date information about the chat. Returns a ChatFullInfo objec... |
| 64 | `getChatAdministrators` | `Array of ChatMember` | chat_id | Use this method to get a list of administrators in a chat. Returns an Array of ChatMember ... |
| 65 | `getChatGifts` | `OwnedGifts` | chat_id | Returns the gifts owned by a chat. Returns OwnedGifts on success. |
| 66 | `getChatMember` | `ChatMember` | chat_id, user_id | Use this method to get information about a member of a chat. The method is only guaranteed... |
| 67 | `getChatMemberCount` | `Integer` | chat_id | Use this method to get the number of members in a chat. Returns Integer on success. |
| 68 | `getChatMenuButton` | `MenuButton` | *None* | Use this method to get the current value of the bot's menu button in a private chat, or th... |
| 69 | `getCustomEmojiStickers` | `Array of Sticker` | custom_emoji_ids | Use this method to get information about custom emoji stickers by their identifiers. Retur... |
| 70 | `getFile` | `File` | file_id | Use this method to get basic information about a file and prepare it for downloading. For ... |
| 71 | `getForumTopicIconStickers` | `Array of Sticker` | *None* | Use this method to get custom emoji stickers, which can be used as a forum topic icon by a... |
| 72 | `getGameHighScores` | `Array of GameHighScore` | user_id | Use this method to get data for high score tables. Will return the score of the specified ... |
| 73 | `getManagedBotAccessSettings` | `BotAccessSettings` | user_id | Use this method to get the access settings of a managed bot. Returns a BotAccessSettings o... |
| 74 | `getManagedBotToken` | `String` | user_id | Use this method to get the token of a managed bot. Returns the token as String on success. |
| 75 | `getMe` | `User` | *None* | A simple method for testing your bot's authentication token. Requires no parameters. Retur... |
| 76 | `getMyCommands` | `Array of BotCommand` | *None* | Use this method to get the current list of the bot's commands for the given scope and user... |
| 77 | `getMyDefaultAdministratorRights` | `ChatAdministratorRights` | *None* | Use this method to get the current default administrator rights of the bot. Returns ChatAd... |
| 78 | `getMyDescription` | `BotDescription` | *None* | Use this method to get the current bot description for the given user language. Returns Bo... |
| 79 | `getMyName` | `BotName` | *None* | Use this method to get the current bot name for the given user language. Returns BotName o... |
| 80 | `getMyShortDescription` | `BotShortDescription` | *None* | Use this method to get the current bot short description for the given user language. Retu... |
| 81 | `getMyStarBalance` | `StarAmount` | *None* | A method to get the current Telegram Stars balance of the bot. Requires no parameters. On ... |
| 82 | `getStarTransactions` | `StarTransactions` | *None* | Returns the bot's Telegram Star transactions in chronological order. On success, returns a... |
| 83 | `getStickerSet` | `StickerSet` | name | Use this method to get a sticker set. On success, a StickerSet object is returned. |
| 84 | `getUpdates` | `Array of Update` | *None* | Use this method to receive incoming updates using long polling (wiki). Returns an Array of... |
| 85 | `getUserChatBoosts` | `UserChatBoosts` | chat_id, user_id | Use this method to get the list of boosts added to a chat by a user. Requires administrato... |
| 86 | `getUserGifts` | `OwnedGifts` | user_id | Returns the gifts owned and hosted by a user. Returns OwnedGifts on success. |
| 87 | `getUserPersonalChatMessages` | `Array of Message` | user_id, limit | Use this method to get the last messages from the personal chat (i.e., the chat currently ... |
| 88 | `getUserProfileAudios` | `UserProfileAudios` | user_id | Use this method to get a list of profile audios for a user. Returns a UserProfileAudios ob... |
| 89 | `getUserProfilePhotos` | `UserProfilePhotos` | user_id | Use this method to get a list of profile pictures for a user. Returns a UserProfilePhotos ... |
| 90 | `getWebhookInfo` | `WebhookInfo` | *None* | Use this method to get current webhook status. Requires no parameters. On success, returns... |
| 91 | `giftPremiumSubscription` | `Boolean` | user_id, month_count, star_count | Gifts a Telegram Premium subscription to the given user. Returns True on success. |
| 92 | `hideGeneralForumTopic` | `Boolean` | chat_id | Use this method to hide the 'General' topic in a forum supergroup chat. The bot must be an... |
| 93 | `leaveChat` | `Boolean` | chat_id | Use this method for your bot to leave a group, supergroup or channel. Returns True on succ... |
| 94 | `logOut` | `Boolean` | *None* | Use this method to log out from the cloud Bot API server before launching the bot locally.... |
| 95 | `pinChatMessage` | `Boolean` | chat_id, message_id | Use this method to add a message to the list of pinned messages in a chat. In private chat... |
| 96 | `postStory` | `Story` | business_connection_id, content, active_period | Posts a story on behalf of a managed business account. Requires the can_manage_stories bus... |
| 97 | `promoteChatMember` | `Boolean` | chat_id, user_id | Use this method to promote or demote a user in a supergroup or a channel. The bot must be ... |
| 98 | `readBusinessMessage` | `Boolean` | business_connection_id, chat_id, message_id | Marks incoming message as read on behalf of a business account. Requires the can_read_mess... |
| 99 | `refundStarPayment` | `Boolean` | user_id, telegram_payment_charge_id | Refunds a successful payment in Telegram Stars. Returns True on success. |
| 100 | `removeBusinessAccountProfilePhoto` | `Boolean` | business_connection_id | Removes the current profile photo of a managed business account. Requires the can_edit_pro... |
| 101 | `removeChatVerification` | `Boolean` | chat_id | Removes verification from a chat that is currently verified on behalf of the organization ... |
| 102 | `removeMyProfilePhoto` | `Boolean` | *None* | Removes the profile photo of the bot. Requires no parameters. Returns True on success. |
| 103 | `removeUserVerification` | `Boolean` | user_id | Removes verification from a user who is currently verified on behalf of the organization r... |
| 104 | `reopenForumTopic` | `Boolean` | chat_id, message_thread_id | Use this method to reopen a closed topic in a forum supergroup chat. The bot must be an ad... |
| 105 | `reopenGeneralForumTopic` | `Boolean` | chat_id | Use this method to reopen a closed 'General' topic in a forum supergroup chat. The bot mus... |
| 106 | `replaceManagedBotToken` | `String` | user_id | Use this method to revoke the current token of a managed bot and generate a new one. Retur... |
| 107 | `replaceStickerInSet` | `Boolean` | user_id, name, old_sticker, sticker | Use this method to replace an existing sticker in a sticker set with a new one. The method... |
| 108 | `repostStory` | `Story` | business_connection_id, from_chat_id, from_story_id, active_period | Reposts a story on behalf of a business account from another business account. Both busine... |
| 109 | `restrictChatMember` | `Boolean` | chat_id, user_id, permissions | Use this method to restrict a user in a supergroup. The bot must be an administrator in th... |
| 110 | `revokeChatInviteLink` | `ChatInviteLink` | chat_id, invite_link | Use this method to revoke an invite link created by the bot. If the primary link is revoke... |
| 111 | `savePreparedInlineMessage` | `PreparedInlineMessage` | user_id, result | Stores a message that can be sent by a user of a Mini App. Returns a PreparedInlineMessage... |
| 112 | `savePreparedKeyboardButton` | `PreparedKeyboardButton` | user_id, button | Stores a keyboard button that can be used by a user within a Mini App. Returns a PreparedK... |
| 113 | `sendAnimation` | `Message` | chat_id, animation | Use this method to send animation files (GIF or H.264/MPEG-4 AVC video without sound). On ... |
| 114 | `sendAudio` | `Message` | chat_id, audio | Use this method to send audio files, if you want Telegram clients to display them in the m... |
| 115 | `sendChatAction` | `Boolean` | chat_id, action | Use this method when you need to tell the user that something is happening on the bot's si... |
| 116 | `sendChatJoinRequestWebApp` | `Boolean` | chat_join_request_query_id, web_app_url | Use this method to process a received chat join request query by showing a Mini App to the... |
| 117 | `sendChecklist` | `Message` | business_connection_id, chat_id, checklist | Use this method to send a checklist on behalf of a connected business account. On success,... |
| 118 | `sendContact` | `Message` | chat_id, phone_number, first_name | Use this method to send phone contacts. On success, the sent Message is returned. |
| 119 | `sendDice` | `Message` | chat_id | Use this method to send an animated emoji that will display a random value. On success, th... |
| 120 | `sendDocument` | `Message` | chat_id, document | Use this method to send general files. On success, the sent Message is returned. Bots can ... |
| 121 | `sendGame` | `Message` | chat_id, game_short_name | Use this method to send a game. On success, the sent Message is returned. |
| 122 | `sendGift` | `Boolean` | gift_id | Sends a gift to the given user or channel chat. The gift can't be converted to Telegram St... |
| 123 | `sendInvoice` | `Message` | chat_id, title, description, payload, currency, prices | Use this method to send invoices. On success, the sent Message is returned. |
| 124 | `sendLivePhoto` | `Message` | chat_id, live_photo, photo | Use this method to send live photos. On success, the sent Message is returned. |
| 125 | `sendLocation` | `Message` | chat_id, latitude, longitude | Use this method to send point on the map. On success, the sent Message is returned. |
| 126 | `sendMediaGroup` | `Array of Message` | chat_id, media | Use this method to send a group of photos, live photos, videos, documents or audios as an ... |
| 127 | `sendMessage` | `Message` | chat_id, text | Use this method to send text messages. On success, the sent Message is returned. |
| 128 | `sendMessageDraft` | `Boolean` | chat_id, draft_id | Use this method to stream a partial message to a user while the message is being generated... |
| 129 | `sendPaidMedia` | `Message` | chat_id, star_count, media | Use this method to send paid media. On success, the sent Message is returned. |
| 130 | `sendPhoto` | `Message` | chat_id, photo | Use this method to send photos. On success, the sent Message is returned. |
| 131 | `sendPoll` | `Message` | chat_id, question, options | Use this method to send a native poll. On success, the sent Message is returned. |
| 132 | `sendRichMessage` | `Message` | chat_id, rich_message | Use this method to send rich messages. If the message contains a block with a media elemen... |
| 133 | `sendRichMessageDraft` | `Boolean` | chat_id, draft_id, rich_message | Use this method to stream a partial rich message to a user while the message is being gene... |
| 134 | `sendSticker` | `Message` | chat_id, sticker | Use this method to send static .WEBP, animated .TGS, or video .WEBM stickers. On success, ... |
| 135 | `sendVenue` | `Message` | chat_id, latitude, longitude, title, address | Use this method to send information about a venue. On success, the sent Message is returne... |
| 136 | `sendVideo` | `Message` | chat_id, video | Use this method to send video files, Telegram clients support MPEG4 videos (other formats ... |
| 137 | `sendVideoNote` | `Message` | chat_id, video_note | Use this method to send a rounded square MPEG4 video of up to 1 minute long. On success, t... |
| 138 | `sendVoice` | `Message` | chat_id, voice | Use this method to send audio files, if you want Telegram clients to display the file as a... |
| 139 | `setBusinessAccountBio` | `Boolean` | business_connection_id | Changes the bio of a managed business account. Requires the can_change_bio business bot ri... |
| 140 | `setBusinessAccountGiftSettings` | `Boolean` | business_connection_id, show_gift_button, accepted_gift_types | Changes the privacy settings pertaining to incoming gifts in a managed business account. R... |
| 141 | `setBusinessAccountName` | `Boolean` | business_connection_id, first_name | Changes the first and last name of a managed business account. Requires the can_change_nam... |
| 142 | `setBusinessAccountProfilePhoto` | `Boolean` | business_connection_id, photo | Changes the profile photo of a managed business account. Requires the can_edit_profile_pho... |
| 143 | `setBusinessAccountUsername` | `Boolean` | business_connection_id | Changes the username of a managed business account. Requires the can_change_username busin... |
| 144 | `setChatAdministratorCustomTitle` | `Boolean` | chat_id, user_id, custom_title | Use this method to set a custom title for an administrator in a supergroup promoted by the... |
| 145 | `setChatDescription` | `Boolean` | chat_id | Use this method to change the description of a group, a supergroup or a channel. The bot m... |
| 146 | `setChatMemberTag` | `Boolean` | chat_id, user_id | Use this method to set a tag for a regular member in a group or a supergroup. The bot must... |
| 147 | `setChatMenuButton` | `Boolean` | *None* | Use this method to change the bot's menu button in a private chat, or the default menu but... |
| 148 | `setChatPermissions` | `Boolean` | chat_id, permissions | Use this method to set default chat permissions for all members. The bot must be an admini... |
| 149 | `setChatPhoto` | `Boolean` | chat_id, photo | Use this method to set a new profile photo for the chat. Photos can't be changed for priva... |
| 150 | `setChatStickerSet` | `Boolean` | chat_id, sticker_set_name | Use this method to set a new group sticker set for a supergroup. The bot must be an admini... |
| 151 | `setChatTitle` | `Boolean` | chat_id, title | Use this method to change the title of a chat. Titles can't be changed for private chats. ... |
| 152 | `setCustomEmojiStickerSetThumbnail` | `Boolean` | name | Use this method to set the thumbnail of a custom emoji sticker set. Returns True on succes... |
| 153 | `setGameScore` | `Message, Boolean` | user_id, score | Use this method to set the score of the specified user in a game message. On success, if t... |
| 154 | `setManagedBotAccessSettings` | `Boolean` | user_id, is_access_restricted | Use this method to change the access settings of a managed bot. Returns True on success. |
| 155 | `setMessageReaction` | `Boolean` | chat_id, message_id | Use this method to change the chosen reactions on a message. Service messages of some type... |
| 156 | `setMyCommands` | `Boolean` | commands | Use this method to change the list of the bot's commands. See this manual for more details... |
| 157 | `setMyDefaultAdministratorRights` | `Boolean` | *None* | Use this method to change the default administrator rights requested by the bot when it's ... |
| 158 | `setMyDescription` | `Boolean` | *None* | Use this method to change the bot's description, which is shown in the chat with the bot i... |
| 159 | `setMyName` | `Boolean` | *None* | Use this method to change the bot's name. Returns True on success. |
| 160 | `setMyProfilePhoto` | `Boolean` | photo | Changes the profile photo of the bot. Returns True on success. |
| 161 | `setMyShortDescription` | `Boolean` | *None* | Use this method to change the bot's short description, which is shown on the bot's profile... |
| 162 | `setPassportDataErrors` | `Boolean` | user_id, errors | Informs a user that some of the Telegram Passport elements they provided contains errors. ... |
| 163 | `setStickerEmojiList` | `Boolean` | sticker, emoji_list | Use this method to change the list of emoji assigned to a regular or custom emoji sticker.... |
| 164 | `setStickerKeywords` | `Boolean` | sticker | Use this method to change search keywords assigned to a regular or custom emoji sticker. T... |
| 165 | `setStickerMaskPosition` | `Boolean` | sticker | Use this method to change the mask position of a mask sticker. The sticker must belong to ... |
| 166 | `setStickerPositionInSet` | `Boolean` | sticker, position | Use this method to move a sticker in a set created by the bot to a specific position. Retu... |
| 167 | `setStickerSetThumbnail` | `Boolean` | name, user_id, format | Use this method to set the thumbnail of a regular or mask sticker set. The format of the t... |
| 168 | `setStickerSetTitle` | `Boolean` | name, title | Use this method to set the title of a created sticker set. Returns True on success. |
| 169 | `setUserEmojiStatus` | `Boolean` | user_id | Changes the emoji status for a given user that previously allowed the bot to manage their ... |
| 170 | `setWebhook` | `Boolean` | url | Use this method to specify a URL and receive incoming updates via an outgoing webhook. Whe... |
| 171 | `stopMessageLiveLocation` | `Message, Boolean` | *None* | Use this method to stop updating a live location message before live_period expires. On su... |
| 172 | `stopPoll` | `Poll` | chat_id, message_id | Use this method to stop a poll which was sent by the bot. On success, the stopped Poll is ... |
| 173 | `transferBusinessAccountStars` | `Boolean` | business_connection_id, star_count | Transfers Telegram Stars from the business account balance to the bot's balance. Requires ... |
| 174 | `transferGift` | `Boolean` | business_connection_id, owned_gift_id, new_owner_chat_id | Transfers an owned unique gift to another user. Requires the can_transfer_and_upgrade_gift... |
| 175 | `unbanChatMember` | `Boolean` | chat_id, user_id | Use this method to unban a previously banned user in a supergroup or channel. The user wil... |
| 176 | `unbanChatSenderChat` | `Boolean` | chat_id, sender_chat_id | Use this method to unban a previously banned channel chat in a supergroup or channel. The ... |
| 177 | `unhideGeneralForumTopic` | `Boolean` | chat_id | Use this method to unhide the 'General' topic in a forum supergroup chat. The bot must be ... |
| 178 | `unpinAllChatMessages` | `Boolean` | chat_id | Use this method to clear the list of pinned messages in a chat. In private chats and chann... |
| 179 | `unpinAllForumTopicMessages` | `Boolean` | chat_id, message_thread_id | Use this method to clear the list of pinned messages in a forum topic in a forum supergrou... |
| 180 | `unpinAllGeneralForumTopicMessages` | `Boolean` | chat_id | Use this method to clear the list of pinned messages in a General forum topic. The bot mus... |
| 181 | `unpinChatMessage` | `Boolean` | chat_id | Use this method to remove a message from the list of pinned messages in a chat. In private... |
| 182 | `upgradeGift` | `Boolean` | business_connection_id, owned_gift_id | Upgrades a given regular gift to a unique gift. Requires the can_transfer_and_upgrade_gift... |
| 183 | `uploadStickerFile` | `File` | user_id, sticker, sticker_format | Use this method to upload a file with a sticker for later use in the createNewStickerSet, ... |
| 184 | `verifyChat` | `Boolean` | chat_id | Verifies a chat on behalf of the organization which is represented by the bot. Returns Tru... |
| 185 | `verifyUser` | `Boolean` | user_id | Verifies a user on behalf of the organization which is represented by the bot. Returns Tru... |
