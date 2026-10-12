# Telegram constraints — verified receipts

*Xero Research Library · 2026-10-12*
*Framing: an addition layer — the limits of one I/O patch (Telegram)
that Zero may use. The platform is not part of Zero.*

Why this file exists: the zero agent's first patch is a Telegram I/O.
These are the platform limits that shape the design, established
in-thread on 2026-10-10 and now cited against Telegram's own docs
(Bot API 10.x, read 2026-10-12).

## 1. The Bot API has no chat-history readback

- A bot receives new activity only as **updates**, delivered by
  long-polling `getUpdates` or by webhook. There is **no Bot API
  method to fetch past messages** from a chat — no `getChatHistory`
  or equivalent exists in the Bot API method list.
- Updates are a perishable queue, not an archive: per the Bot API
  reference, incoming updates are stored on the server until the bot
  collects them, "but they will not be kept longer than 24 hours."
- Design consequence (already load-bearing in Xero): the bot must
  keep its own ledger of everything it has seen. If the agent didn't
  write it to its files, it doesn't know it. History is a local
  artifact, never a platform service.
- Source: https://core.telegram.org/bots/api (Getting updates)

## 2. Bots do not (by default) see other bots' messages

- Telegram's own features doc: on Telegram, bots generally **cannot
  see** messages from other bots.
- There is now an opt-in exception: **Bot-to-Bot Communication Mode**,
  enabled per-bot in @BotFather. With it, in groups a bot can receive
  another bot's message when *mentioned* in a command
  (`/command@OtherBot`) or *replied to* directly; a bot with the mode
  enabled that is also a group admin (or has group privacy mode off)
  receives all other bots' group messages. Since Bot API 10.0, bots
  can also DM another bot by username if **both** enabled the mode.
- Telegram explicitly warns that bot-to-bot setups can produce
  infinite interaction loops and require termination safeguards.
- Design consequence: "no native bot-to-bot" was the 2026-10-10
  finding and is still the default posture. Bot-to-bot is now
  *possible* but is an opt-in, per-bot configuration with loop risk —
  a deliberate contract, not an ambient property of a group chat.
- Sources: https://core.telegram.org/bots/features/ (Bot-to-Bot
  Communication; Privacy Mode); https://core.telegram.org/bots/api
  (Bot API 10.0 changelog)

## 3. Group privacy mode limits what a bot receives

- **Privacy mode is enabled by default** for all bots in groups
  (exception: bots added as group admins receive all messages).
- With privacy mode on, a bot in a group only receives: commands
  addressed to it, replies to its own messages, mentions, and certain
  service messages — not the general flow of the chat.
- Disabling privacy mode makes the bot receive all group messages
  like an ordinary member; the change requires the bot to be removed
  and re-added to the group to take effect.
- Design consequence: a Xero agent in a group chat is deaf by default
  except when addressed. Ambient listening is a conscious
  configuration act (and a consent decision about the room).
- Source: https://core.telegram.org/bots/features/ (Privacy Mode)

## 4. History fetch exists only on the client (MTProto) side

- Reading old messages (e.g., `messages.getHistory`) is a feature of
  the **client API / MTProto** — the protocol the Telegram apps and
  user-account libraries (TDLib, Telethon, Pyrogram) speak. It is
  not part of the Bot API at all.
- Using it means authenticating **as a user** (phone number + session
  file), which is a different trust and ToS posture from running a
  bot: a session file is effectively a logged-in human credential.
- Design consequence: "just read the history" always smuggles in a
  user account. Xero's stance — the agent's memory is its own files,
  deposited as events arrive — is not a workaround; it's the only
  architecture the bot surface actually supports.
- Sources: https://core.telegram.org/bots/api (method list contains
  no history method); corroborating design write-ups:
  https://github.com/passioncode-ai/fabric/blob/HEAD/docs/adr/0037-the-telegram-bot-answers-by-reply-and-fabric-has-no-always-on-process.md and https://dev.to/starnikovoleg/the-telegram-bot-api-cannot-read-a-channel-your-bot-is-not-in-4jme

## One-line summary for builders

Telegram gives a bot a 24-hour perishable update queue, addressed-only
hearing in groups by default, and no past. Everything else —
memory, history, other agents — the agent must build and keep itself.

*Status: high confidence; all four constraints verified against
core.telegram.org on 2026-10-12. Watch item: the bot-to-bot surface
is new (Bot API 10.0, 2026) and still expanding — re-check before
designing any multi-bot Telegram topology.*
