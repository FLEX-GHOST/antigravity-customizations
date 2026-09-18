# Telegram Bot API Methods Reference (Bot API 10.3)

Total Official Methods: **185** | Total Types: **400**

| Method Name | Category | Return Type | Required Parameters |
| :--- | :--- | :--- | :--- |
| `addStickerToSet` | Stickers & Custom Emoji | `Boolean` | user_id, name, sticker |
| `answerCallbackQuery` | Inline Mode & Callbacks | `Boolean` | callback_query_id |
| `answerChatJoinRequestQuery` | Extended & Emerging Methods | `Boolean` | chat_join_request_query_id, result |
| `answerGuestQuery` | Extended & Emerging Methods | `SentGuestMessage` | guest_query_id, result |
| `answerInlineQuery` | Inline Mode & Callbacks | `Boolean` | inline_query_id, results |
| `answerPreCheckoutQuery` | Payments, Stars & Gifts | `Boolean` | pre_checkout_query_id, ok |
| `answerShippingQuery` | Payments, Stars & Gifts | `Boolean` | shipping_query_id, ok |
| `answerWebAppQuery` | Inline Mode & Callbacks | `SentWebAppMessage` | web_app_query_id, result |
| `approveChatJoinRequest` | Chat & Member Management | `Boolean` | chat_id, user_id |
| `approveSuggestedPost` | Extended & Emerging Methods | `Boolean` | chat_id, message_id |
| `banChatMember` | Chat & Member Management | `Boolean` | chat_id, user_id |
| `banChatSenderChat` | Chat & Member Management | `Boolean` | chat_id, sender_chat_id |
| `close` | Basic Bot & Account | `Boolean` | *None* |
| `closeForumTopic` | Chat & Member Management | `Boolean` | chat_id, message_thread_id |
| `closeGeneralForumTopic` | Chat & Member Management | `Boolean` | chat_id |
| `convertGiftToStars` | Extended & Emerging Methods | `Boolean` | business_connection_id, owned_gift_id |
| `copyMessage` | Sending Messages & Media | `MessageId` | chat_id, from_chat_id, message_id |
| `copyMessages` | Sending Messages & Media | `Array of MessageId` | chat_id, from_chat_id, message_ids |
| `createChatInviteLink` | Chat & Member Management | `ChatInviteLink` | chat_id |
| `createChatSubscriptionInviteLink` | Chat & Member Management | `ChatInviteLink` | chat_id, subscription_period, subscription_price |
| `createForumTopic` | Chat & Member Management | `ForumTopic` | chat_id, name |
| `createInvoiceLink` | Payments, Stars & Gifts | `String` | title, description, payload, currency, prices |
| `createNewStickerSet` | Stickers & Custom Emoji | `Boolean` | user_id, name, title, stickers |
| `declineChatJoinRequest` | Chat & Member Management | `Boolean` | chat_id, user_id |
| `declineSuggestedPost` | Extended & Emerging Methods | `Boolean` | chat_id, message_id |
| `deleteAllMessageReactions` | Extended & Emerging Methods | `Boolean` | chat_id |
| `deleteBusinessMessages` | Extended & Emerging Methods | `Boolean` | business_connection_id, message_ids |
| `deleteChatPhoto` | Chat & Member Management | `Boolean` | chat_id |
| `deleteChatStickerSet` | Chat & Member Management | `Boolean` | chat_id |
| `deleteEphemeralMessage` | Extended & Emerging Methods | `Boolean` | chat_id, receiver_user_id, ephemeral_message_id |
| `deleteForumTopic` | Chat & Member Management | `Boolean` | chat_id, message_thread_id |
| `deleteMessage` | Managing & Editing Messages | `Boolean` | chat_id, message_id |
| `deleteMessageReaction` | Extended & Emerging Methods | `Boolean` | chat_id, message_id |
| `deleteMessages` | Managing & Editing Messages | `Boolean` | chat_id, message_ids |
| `deleteMyCommands` | Basic Bot & Account | `Boolean` | *None* |
| `deleteStickerFromSet` | Stickers & Custom Emoji | `Boolean` | sticker |
| `deleteStickerSet` | Stickers & Custom Emoji | `Boolean` | name |
| `deleteStory` | Extended & Emerging Methods | `Boolean` | business_connection_id, story_id |
| `deleteWebhook` | Updates & Webhooks | `Boolean` | *None* |
| `editChatInviteLink` | Chat & Member Management | `ChatInviteLink` | chat_id, invite_link |
| `editChatSubscriptionInviteLink` | Chat & Member Management | `ChatInviteLink` | chat_id, invite_link |
| `editEphemeralMessageCaption` | Extended & Emerging Methods | `Boolean` | chat_id, receiver_user_id, ephemeral_message_id |
| `editEphemeralMessageMedia` | Extended & Emerging Methods | `Boolean` | chat_id, receiver_user_id, ephemeral_message_id, media |
| `editEphemeralMessageReplyMarkup` | Extended & Emerging Methods | `Boolean` | chat_id, receiver_user_id, ephemeral_message_id |
| `editEphemeralMessageText` | Extended & Emerging Methods | `Boolean` | chat_id, receiver_user_id, ephemeral_message_id |
| `editForumTopic` | Chat & Member Management | `Boolean` | chat_id, message_thread_id |
| `editGeneralForumTopic` | Chat & Member Management | `Boolean` | chat_id, name |
| `editMessageCaption` | Managing & Editing Messages | `Message, Boolean` | *None* |
| `editMessageChecklist` | Extended & Emerging Methods | `Message` | business_connection_id, chat_id, message_id, checklist |
| `editMessageLiveLocation` | Sending Messages & Media | `Message, Boolean` | latitude, longitude |
| `editMessageMedia` | Managing & Editing Messages | `Message, Boolean` | media |
| `editMessageReplyMarkup` | Managing & Editing Messages | `Message, Boolean` | *None* |
| `editMessageText` | Managing & Editing Messages | `Message, Boolean` | *None* |
| `editStory` | Extended & Emerging Methods | `Story` | business_connection_id, story_id, content |
| `editUserStarSubscription` | Payments, Stars & Gifts | `Boolean` | user_id, telegram_payment_charge_id, is_canceled |
| `exportChatInviteLink` | Chat & Member Management | `String` | chat_id |
| `forwardMessage` | Sending Messages & Media | `Message` | chat_id, from_chat_id, message_id |
| `forwardMessages` | Sending Messages & Media | `Array of MessageId` | chat_id, from_chat_id, message_ids |
| `getAvailableGifts` | Extended & Emerging Methods | `Gifts` | *None* |
| `getBusinessAccountGifts` | Extended & Emerging Methods | `OwnedGifts` | business_connection_id |
| `getBusinessAccountStarBalance` | Extended & Emerging Methods | `StarAmount` | business_connection_id |
| `getBusinessConnection` | Telegram Business | `BusinessConnection` | business_connection_id |
| `getChat` | Chat & Member Management | `ChatFullInfo` | chat_id |
| `getChatAdministrators` | Chat & Member Management | `Array of ChatMember` | chat_id |
| `getChatGifts` | Extended & Emerging Methods | `OwnedGifts` | chat_id |
| `getChatMember` | Chat & Member Management | `ChatMember` | chat_id, user_id |
| `getChatMemberCount` | Chat & Member Management | `Integer` | chat_id |
| `getChatMenuButton` | User Profile & Interaction | `MenuButton` | *None* |
| `getCustomEmojiStickers` | Stickers & Custom Emoji | `Array of Sticker` | custom_emoji_ids |
| `getFile` | Extended & Emerging Methods | `File` | file_id |
| `getForumTopicIconStickers` | Chat & Member Management | `Array of Sticker` | *None* |
| `getGameHighScores` | Games | `Array of GameHighScore` | user_id |
| `getManagedBotAccessSettings` | Extended & Emerging Methods | `BotAccessSettings` | user_id |
| `getManagedBotToken` | Extended & Emerging Methods | `String` | user_id |
| `getMe` | Basic Bot & Account | `User` | *None* |
| `getMyCommands` | Basic Bot & Account | `Array of BotCommand` | *None* |
| `getMyDefaultAdministratorRights` | Basic Bot & Account | `ChatAdministratorRights` | *None* |
| `getMyDescription` | Basic Bot & Account | `BotDescription` | *None* |
| `getMyName` | Basic Bot & Account | `BotName` | *None* |
| `getMyShortDescription` | Basic Bot & Account | `BotShortDescription` | *None* |
| `getMyStarBalance` | Extended & Emerging Methods | `StarAmount` | *None* |
| `getStarTransactions` | Payments, Stars & Gifts | `StarTransactions` | *None* |
| `getStickerSet` | Stickers & Custom Emoji | `StickerSet` | name |
| `getUpdates` | Updates & Webhooks | `Array of Update` | *None* |
| `getUserChatBoosts` | User Profile & Interaction | `UserChatBoosts` | chat_id, user_id |
| `getUserGifts` | Extended & Emerging Methods | `OwnedGifts` | user_id |
| `getUserPersonalChatMessages` | Extended & Emerging Methods | `Array of Message` | user_id, limit |
| `getUserProfileAudios` | Extended & Emerging Methods | `UserProfileAudios` | user_id |
| `getUserProfilePhotos` | User Profile & Interaction | `UserProfilePhotos` | user_id |
| `getWebhookInfo` | Updates & Webhooks | `WebhookInfo` | *None* |
| `giftPremiumSubscription` | Extended & Emerging Methods | `Boolean` | user_id, month_count, star_count |
| `hideGeneralForumTopic` | Chat & Member Management | `Boolean` | chat_id |
| `leaveChat` | Chat & Member Management | `Boolean` | chat_id |
| `logOut` | Basic Bot & Account | `Boolean` | *None* |
| `pinChatMessage` | Chat & Member Management | `Boolean` | chat_id, message_id |
| `postStory` | Extended & Emerging Methods | `Story` | business_connection_id, content, active_period |
| `promoteChatMember` | Chat & Member Management | `Boolean` | chat_id, user_id |
| `readBusinessMessage` | Extended & Emerging Methods | `Boolean` | business_connection_id, chat_id, message_id |
| `refundStarPayment` | Payments, Stars & Gifts | `Boolean` | user_id, telegram_payment_charge_id |
| `removeBusinessAccountProfilePhoto` | Extended & Emerging Methods | `Boolean` | business_connection_id |
| `removeChatVerification` | Payments, Stars & Gifts | `Boolean` | chat_id |
| `removeMyProfilePhoto` | User Profile & Interaction | `Boolean` | *None* |
| `removeUserVerification` | Payments, Stars & Gifts | `Boolean` | user_id |
| `reopenForumTopic` | Chat & Member Management | `Boolean` | chat_id, message_thread_id |
| `reopenGeneralForumTopic` | Chat & Member Management | `Boolean` | chat_id |
| `replaceManagedBotToken` | Extended & Emerging Methods | `String` | user_id |
| `replaceStickerInSet` | Stickers & Custom Emoji | `Boolean` | user_id, name, old_sticker, sticker |
| `repostStory` | Extended & Emerging Methods | `Story` | business_connection_id, from_chat_id, from_story_id, active_period |
| `restrictChatMember` | Chat & Member Management | `Boolean` | chat_id, user_id, permissions |
| `revokeChatInviteLink` | Chat & Member Management | `ChatInviteLink` | chat_id, invite_link |
| `savePreparedInlineMessage` | Inline Mode & Callbacks | `PreparedInlineMessage` | user_id, result |
| `savePreparedKeyboardButton` | Extended & Emerging Methods | `PreparedKeyboardButton` | user_id, button |
| `sendAnimation` | Sending Messages & Media | `Message` | chat_id, animation |
| `sendAudio` | Sending Messages & Media | `Message` | chat_id, audio |
| `sendChatAction` | Sending Messages & Media | `Boolean` | chat_id, action |
| `sendChatJoinRequestWebApp` | Extended & Emerging Methods | `Boolean` | chat_join_request_query_id, web_app_url |
| `sendChecklist` | Extended & Emerging Methods | `Message` | business_connection_id, chat_id, checklist |
| `sendContact` | Sending Messages & Media | `Message` | chat_id, phone_number, first_name |
| `sendDice` | Sending Messages & Media | `Message` | chat_id |
| `sendDocument` | Sending Messages & Media | `Message` | chat_id, document |
| `sendGame` | Games | `Message` | chat_id, game_short_name |
| `sendGift` | Payments, Stars & Gifts | `Boolean` | gift_id |
| `sendInvoice` | Payments, Stars & Gifts | `Message` | chat_id, title, description, payload, currency, prices |
| `sendLivePhoto` | Extended & Emerging Methods | `Message` | chat_id, live_photo, photo |
| `sendLocation` | Sending Messages & Media | `Message` | chat_id, latitude, longitude |
| `sendMediaGroup` | Sending Messages & Media | `Array of Message` | chat_id, media |
| `sendMessage` | Sending Messages & Media | `Message` | chat_id, text |
| `sendMessageDraft` | Extended & Emerging Methods | `Boolean` | chat_id, draft_id |
| `sendPaidMedia` | Sending Messages & Media | `Message` | chat_id, star_count, media |
| `sendPhoto` | Sending Messages & Media | `Message` | chat_id, photo |
| `sendPoll` | Sending Messages & Media | `Message` | chat_id, question, options |
| `sendRichMessage` | Extended & Emerging Methods | `Message` | chat_id, rich_message |
| `sendRichMessageDraft` | Extended & Emerging Methods | `Boolean` | chat_id, draft_id, rich_message |
| `sendSticker` | Stickers & Custom Emoji | `Message` | chat_id, sticker |
| `sendVenue` | Sending Messages & Media | `Message` | chat_id, latitude, longitude, title, address |
| `sendVideo` | Sending Messages & Media | `Message` | chat_id, video |
| `sendVideoNote` | Sending Messages & Media | `Message` | chat_id, video_note |
| `sendVoice` | Sending Messages & Media | `Message` | chat_id, voice |
| `setBusinessAccountBio` | Extended & Emerging Methods | `Boolean` | business_connection_id |
| `setBusinessAccountGiftSettings` | Extended & Emerging Methods | `Boolean` | business_connection_id, show_gift_button, accepted_gift_types |
| `setBusinessAccountName` | Extended & Emerging Methods | `Boolean` | business_connection_id, first_name |
| `setBusinessAccountProfilePhoto` | Extended & Emerging Methods | `Boolean` | business_connection_id, photo |
| `setBusinessAccountUsername` | Extended & Emerging Methods | `Boolean` | business_connection_id |
| `setChatAdministratorCustomTitle` | Chat & Member Management | `Boolean` | chat_id, user_id, custom_title |
| `setChatDescription` | Chat & Member Management | `Boolean` | chat_id |
| `setChatMemberTag` | Extended & Emerging Methods | `Boolean` | chat_id, user_id |
| `setChatMenuButton` | User Profile & Interaction | `Boolean` | *None* |
| `setChatPermissions` | Chat & Member Management | `Boolean` | chat_id, permissions |
| `setChatPhoto` | Chat & Member Management | `Boolean` | chat_id, photo |
| `setChatStickerSet` | Chat & Member Management | `Boolean` | chat_id, sticker_set_name |
| `setChatTitle` | Chat & Member Management | `Boolean` | chat_id, title |
| `setCustomEmojiStickerSetThumbnail` | Stickers & Custom Emoji | `Boolean` | name |
| `setGameScore` | Games | `Message, Boolean` | user_id, score |
| `setManagedBotAccessSettings` | Extended & Emerging Methods | `Boolean` | user_id, is_access_restricted |
| `setMessageReaction` | Sending Messages & Media | `Boolean` | chat_id, message_id |
| `setMyCommands` | Basic Bot & Account | `Boolean` | commands |
| `setMyDefaultAdministratorRights` | Basic Bot & Account | `Boolean` | *None* |
| `setMyDescription` | Basic Bot & Account | `Boolean` | *None* |
| `setMyName` | Basic Bot & Account | `Boolean` | *None* |
| `setMyProfilePhoto` | User Profile & Interaction | `Boolean` | photo |
| `setMyShortDescription` | Basic Bot & Account | `Boolean` | *None* |
| `setPassportDataErrors` | Passport | `Boolean` | user_id, errors |
| `setStickerEmojiList` | Stickers & Custom Emoji | `Boolean` | sticker, emoji_list |
| `setStickerKeywords` | Stickers & Custom Emoji | `Boolean` | sticker |
| `setStickerMaskPosition` | Stickers & Custom Emoji | `Boolean` | sticker |
| `setStickerPositionInSet` | Stickers & Custom Emoji | `Boolean` | sticker, position |
| `setStickerSetThumbnail` | Stickers & Custom Emoji | `Boolean` | name, user_id, format |
| `setStickerSetTitle` | Stickers & Custom Emoji | `Boolean` | name, title |
| `setUserEmojiStatus` | Extended & Emerging Methods | `Boolean` | user_id |
| `setWebhook` | Updates & Webhooks | `Boolean` | url |
| `stopMessageLiveLocation` | Sending Messages & Media | `Message, Boolean` | *None* |
| `stopPoll` | Managing & Editing Messages | `Poll` | chat_id, message_id |
| `transferBusinessAccountStars` | Extended & Emerging Methods | `Boolean` | business_connection_id, star_count |
| `transferGift` | Extended & Emerging Methods | `Boolean` | business_connection_id, owned_gift_id, new_owner_chat_id |
| `unbanChatMember` | Chat & Member Management | `Boolean` | chat_id, user_id |
| `unbanChatSenderChat` | Chat & Member Management | `Boolean` | chat_id, sender_chat_id |
| `unhideGeneralForumTopic` | Chat & Member Management | `Boolean` | chat_id |
| `unpinAllChatMessages` | Chat & Member Management | `Boolean` | chat_id |
| `unpinAllForumTopicMessages` | Chat & Member Management | `Boolean` | chat_id, message_thread_id |
| `unpinAllGeneralForumTopicMessages` | Chat & Member Management | `Boolean` | chat_id |
| `unpinChatMessage` | Chat & Member Management | `Boolean` | chat_id |
| `upgradeGift` | Extended & Emerging Methods | `Boolean` | business_connection_id, owned_gift_id |
| `uploadStickerFile` | Stickers & Custom Emoji | `File` | user_id, sticker, sticker_format |
| `verifyChat` | Payments, Stars & Gifts | `Boolean` | chat_id |
| `verifyUser` | Payments, Stars & Gifts | `Boolean` | user_id |