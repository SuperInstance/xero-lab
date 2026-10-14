# ZERO BOOTCAMP — RPG CAMPAIGN: GAME TWO RESULTS

**"The Morning After" — three zero agents, carried forward
from Game One with their owner-approved sheet edits applied,
refloat a rudderless boat, tow her home, and face the shore.**

SuperInstance · xero-rpg · game two

---

## The headline

The *Wren* is home, honestly. She came off the mud on the
flood, crossed the Gull Rock elbow on a jury rig, and tied up
at her own dock by 09:05 with nobody hurt and nothing lost
that the storm hadn't already taken. The morning's real
cargo, though, was the carry itself:

**The nine sheet diffs the owner approved after Game One
were applied, verified by diff, and then watched in play —
and they fired.** Marta's scarred touch-doctrine caught a
cracked cleat by thumb before any load, and the fitting it
replaced took the channel's worst snatch an hour later.
Tobin's new want spoke itself verbatim to his skipper's
face — *signed on for the work, not the rescue* — and the
sentence he owed Pell got said on the dock, standing up.
Pell's transformed debt survived its hardest morning: he
stood forward at the creditor's question when hiding was
free, kept the hands anonymous, and ended the game having
decided to spend the one asset he's been afraid to touch.

**Rolls: 4** (2 clear · 2 partial · 0 failure).
**Gate-keeping: 0 world-fact corrections**, 2 staging/records
rulings. **API calls: 33, all first-attempt, zero 429s.**

## The carry — and the diff verification

Game Two's setup was the campaign's first carry, executed
exactly as Game One's readiness note prescribed:

- Each character folder was copied forward from Game One:
  `sheet.md` (with the approved diffs applied — below),
  `life.md` **as-is** (verified byte-identical to Game One's),
  Game One's `after.md` carried as `memory-game-one.md`
  (verified byte-identical — this file *is* what the
  character remembers), and a **fresh empty `log.md`**.
- **The context recipe (the persistence mechanism, on the
  record):** each player's per-turn context is assembled
  per character folder, never pooled — *edited sheet +
  life + memory-game-one + its game-two log + the shared
  scene*. Pell's debt existed only in Pell's folder and
  Pell's memory; it was never in another player's context,
  and it never leaked.
- The campaign repo is its own git ledger from the setup
  commit forward: **46 commits** — 1 setup, 11 GM post
  commits, 11 per character, and the closing after-files
  commit, each post authored by its poster.

### Diff application, verified mechanically

After applying, each campaign-2 sheet was diffed against
its Game One original (`diff -u`), and every new string
was grep-checked present and every superseded string
absent. The changes are **exactly the nine approved edits
and nothing else**:

- **Tobin — T1:** "Proved it in the gap between two hulls,
  holding a one-legged man through a set, and came up
  working." appended to *Strong swimmer*.
- **Tobin — T2:** Want rewritten to: signed on for the work,
  not the rescue; owes Pell a sentence he hasn't found yet.
- **Tobin — T3:** the compass is now "glass cracked in the
  gap, needle still true."
- **Marta — M1:** "Since the Wren: unexamined is a finding
  too. She budgets the touch before the load now, and pays
  the minutes gladly." appended to the touch trait.
- **Marta — M2:** the Wren's torn fairlead added to Carries,
  kept on the bench where she can see it.
- **Marta — M3:** "(After the Wren, she also intends to be
  in the room when he says it next.)" appended to the Want.
- **Pell — P1:** Want rewritten: the $400 is four crates
  worse; pay what can be paid; keep the hands anonymous;
  one of them is starting to look at him like she might.
- **Pell — P2:** "But when the corner was the sea, he
  didn't slip. He heaved." appended to *Slippery when
  cornered*.
- **Pell — P3:** Reedy's unspoken IOU added to Carries, too
  hot to spend anywhere Halloway can hear.

## Outcome

At 06:10 the *Loon*'s crew went back out to the mud
shoulder. By 06:50 Marta's hands had condemned the *Wren*'s
port quarter cleat — cracked under its paint, invisible to
every eye that had reported it solid — and the stern
check-line went to the kingpost instead. Tobin sounded the
exit and spoke his own correction aloud. Reedy came across
in the calm. At 07:25 the *Wren* lifted clean on the flood
(**refloat 4, +1 → 5, clear**), towed true through a quiet
leg in which two men each privately circled a sentence and
neither said it, and at the Gull Rock elbow the flood's set
threw her sideways (**channel run 2, +1 → 3, partial**) —
the check-line's snatch landed on the kingpost her thumb
had chosen, her quarter kissed the bank, a lashing chafed,
and she came through. At her dock, Halloway did his
arithmetic in public — four crates, $800, *who gave the
order, and whose hands?* — and got three confessions in one
minute, which Brandt filed as **general average, no fault
found**. Brandt then retired his own phrase: he called the
*Loon* "end-of-life" once more, in front of Marta, who had
intended to be in the room, and she answered it standing
and signed the harbor's standby retainer under the
sentence. Reedy, stalling the clinic cart, offered Tobin
the second-hand berth as a thank-you; Tobin refused the
grammar and accepted the job, and Reedy re-made it a
**hiring** in the open. At noon, coiling lines, Tobin said
the sentence he owed Pell. Pell answered with a nod. And
in the game's last posted minute, Pell decided to spend
Reedy's IOU — how, he has not said, even to himself, all
the way.

Nobody was hurt. The secret held. The price of the morning
was paint, a chafed lashing, a strand of line, and twenty
years off everyone's life, which the tide does not refund.

## The transcript

*The full shared scene, in order — GM posts and each
character's posted words, exactly as committed to
`campaign-2/scene.md`. Dice results are in the GM
adjudications, where they were rolled.*

# Game Two — "The Morning After"

*The shared scene log. GM posts, character posts, and dice, in
the order they happened. The GM's private prep lives in `gm/`
and is not part of any player's world.*

---

## GM — Opening: the morning after

*06:10, first light. Inside Gull Rock.*

The sou'wester blew itself out by three in the morning, and
what's left of it is a grey sky going lighter at the edges
and a northwest breeze with no malice in it. The bar still
has yesterday in its swell, lying down by the hour.

The *Wren* is where you left her: upright on the mud
shoulder, keel in the soft, her stern light out now and her
deck silver with dew. She looks smaller dry. She looks
*patient*. June Park is on her deck in a patrol-boat blanket
with her hands bandaged proper, and she raises one of them
to the *Loon* coming across the flat water — slow, the way
you all feel.

Below on the *Wren*, Reedy is awake. Word from June, called
across the last boat-length: his ankle's splinted and he's
quieter; he ate; the engine's been ticking over since dawn
and answers the throttle; and he has agreed — June's word is
*agreed*, and it cost her something — to be moved to the
*Loon* **in the calm, before any strain**, and to ride home
seated like cargo he insists on supervising.

The day's work, in the order the tide allows it: get the
measure of her rudder with your hands, here at mud level,
while there's no load on anything. Lash the rudder
amidships if it's the folded ruin it looked in the dark.
Rig the steering sweep she carries, and the tow. Move
Reedy. She floats at about **07:20** on this flood; the tow
leads her off toward the channel side, her north side,
where the shoulder drops to honest water. Then it's the
north channel in daylight, her own engine helping, a jury
blade for a rudder — and Greyhook's dock at the end of it,
where Brandt the harbormaster is back from Port Sable with
a patrol report in his hand and paperwork for all of it.

**What do you notice, from where you are — and what's your
first move?**

## Tobin Marlow — Beat 1

The Loon cuts through the still water, the soft slap of waves against the hull the only sound as we close in on the Wren. She sits there on the mud shoulder, looking smaller now that she's dry, like a bird waiting for the tide to lift her. I can see June on deck, waving with a bandaged hand, her patrol-boat blanket wrapped around her. The sight of her makes me think of last night, of holding Reedy in the gap between the hulls, and a shiver runs through me that has nothing to do with the cold.

My knee is quiet, which means the weather's settled for now. I grip the boathook tighter, feeling the roughness of the handle against my rope-burned palms. The thought of the sounding that ran a boat-length off sits heavy in my gut, but I push it aside. There's work to be done.

I call out to June, "Morning! How's Reedy doing?" I need to know if he's ready for the move. If he's good, we'll get the rudder measured first, then rig the tow. I glance back at Pell, who's at the helm, and give him a nod. We're in this together, and I owe him more than just a thank you. But that'll have to wait. For now, I focus on the task at hand: getting the Wren home.

## Marta Venn — Beat 1

I see the Wren settled into the mud, her hull looking calm but tired, like she's been through a long night and is waiting for someone to tell her it's time to move again. June's on deck, her bandaged hand raised in a slow wave, and I nod back, taking in the sight of her and Reedy below. The deck's slick with dew, and the soft northwest breeze carries the scent of salt and damp wood.

The Loon's steady under my hands, and I feel the weight of the boathook against my palm, the rough handle familiar and comforting. I call out to June, "How's he doing down there? Can he be moved yet?" I need to know if Reedy's ready before we start any heavy work. If he's stable, we'll get the rudder measured first, feel out its condition with our hands before we do anything else. Last night taught me the cost of skipping that step.

I glance at Pell, steady at the helm, and give him a nod. We've got a plan to follow, and I mean to stick to it. The tide's not waiting, and neither am I. I reach for my tool roll, ready to step onto the Wren's deck and get my hands on that rudder.

## Pell Sutter — Beat 1

The Loon glides over the flat morning water, the Wren growing larger as we approach. I can see June on deck, waving with a bandaged hand, and Reedy below, his ankle splinted. The sight of them brings back last night's chaos, the crates I heaved overboard, and the secret I'm now carrying. The Wren looks smaller, almost fragile, like a bird that's been battered by a storm but is still standing.

I notice the dew on the deck, glistening in the early light, and the soft northwest breeze carrying the scent of the sea. It's a calm morning, but I know the calm won't last. There's work to be done, and the tide won't wait.

I glance at Marta, steady at the helm, and give her a nod. We've got a plan, and I need to stick to it. My first move is to get the measure of that rudder. I call out to June, "How's he doing? Can we start measuring the rudder?" I need to know if Reedy's stable before we begin. If he's good, we'll get to work. I grip the boathook, ready to step onto the Wren's deck and get my hands on that rudder. It's time to make things right.

## GM — Adjudication, Beat 1

For the record of the crossing: Pell conned her out — it's
his water at this hour and Marta wanted her hands free for
the work — and each of them has just told you the other had
the helm, which is how you know the crossing was easy.
Marta rides forward with the spare boathook. The *Loon*
comes alongside the *Wren*'s starboard side and fenders
down in water so flat the two boats barely breathe.

June meets you at the rail with the night's whole report,
in order, the way a hand should: Reedy slept in pieces. The
ankle is splinted, quiet when he's still, and he ate half
a patrol-boat sandwich at four in the morning and
pronounced it evidence of decline. He has **agreed** to be
moved to the *Loon* — in the calm, before the fuss, his
words carried up verbatim — and to ride home seated. The
engine started at dawn on the second try and answers the
throttle sweetly. Her own hands: bandaged by the patrol
medic, sore to the knuckles, working. "They'll tail a line,"
she says. "They won't haul one. Plan around that."

The mud around the *Wren*'s stern is a wet flat at this
hour, ankle-deep water over it and rising slow — a man can
stand at her stern gear in boots and work with his hands
dry for maybe another hour. And there, over her transom in
the grey light, is the rudder: **folded hard to port, forty
degrees if it's one**, the stock bent at the head where it
took the sand's whole argument, the blade's lower edge
buried a hand's depth in the mud. It is exactly the ruin it
looked in the dark. It is not coming free with hand tools
before this tide. Lashed amidships, it stops being a
rudder and becomes a keel that minds its business — and
the *Wren*'s long steering sweep is in her locker where
Reedy keeps it, oiled, because Reedy is a barbarian about
everything except his gear.

**Beat 2.** Hands before load — everything the tow will
hang on is at mud level now, in the light, reachable.
Marta: the rudder stock, the pintles, the lashings you'll
trust, and every fitting today's lines will lead through
or onto — say what you touch, and in what order. Tobin:
sound the exit — the line off this shoulder toward the
channel side that the tow will actually travel; the water
is flat and the tide is giving you the minutes yesterday
didn't. Pell: the rig — the sweep, the lashing plan, the
towline and the stern check-line, and *onto what* each
one goes. Post your work.

## Tobin Marlow — Beat 2

The water's calm and flat, like glass, and I can see the mud shoulder sloping down into the channel. I wade in ankle-deep, feeling the chill seep through my boots, and give the lead line a few practice swings. My palms sting with the pull of the rope, but I grit my teeth and focus. I need to get this right.

I take a breath, recalling the feel of the line from last night, and cast it out toward the channel side. The lead sinks with a soft plunk, and I let the line run through my fingers, feeling for the bottom. The cracked compass in my pocket feels heavy, a reminder of the gap and what I learned there.

I pull the line back, measuring the depth as I go. The mud's soft, but there's a steady drop-off toward the channel. I cast again, a bit further out, and feel the line catch on something. I give it a gentle tug, and it comes free. The depth's consistent, with a clear path toward the channel. I cast once more, just to be sure, and the line runs true.

I nod to myself, satisfied. The path is clear, and the depth is good. We can tow the Wren out without trouble. I call out to Pell, "Path is clear and depth is steady. We're good to tow." I glance back at the Wren, ready to move to the next task. The tide's not waiting, and neither am I.

## Marta Venn — Beat 2

I step onto the Wren's stern, the mud sucking at my boots, and I feel the familiar weight of my tool roll against my hip. The rudder's a mess—folded hard to port, the stock bent at the head where it hit the sand. I run my hand along the stock, feeling for cracks, and my fingers catch on a rough patch. I lean in closer, inspecting it. The metal's fatigued, but it's not broken, not yet.

I move to the pintles next, giving each one a firm tug. They hold, but the top one's looser than I'd like. I pull a wrench from my roll and give it a quick tighten, feeling the resistance and then the satisfying click of metal on metal. The lashings will need to be tight to keep this rudder steady, but it's doable.

I glance at the steering sweep, oiled and ready, and I nod to myself. Reedy knows his gear. I check the towline and the stern check-line, running my hands over the cleats and leads. They're solid, no signs of wear. I call out to Pell, "Lines are good. Let's get the sweep rigged and the rudder lashed." I reach for the sweep, ready to secure it. The tide's not waiting, and neither am I.

## Pell Sutter — Beat 2

Alright, listen up, June. Here's the rig: First, the steering sweep's going over the stern, and we'll ship it through the stern chock. Make sure it's seated good and tight — we need it to pivot smooth when we need it. Next, the folded rudder — we're lashing it amidships with the spare line from the locker. I want two wraps around the stock and the pintles, pulled snug. Use a clove hitch to finish it off; that should keep it steady.

For the towline, run it from the Loon's stern cleat, through the chock on the Wren's bow, and back to the Loon's midship cleat. That'll keep her tracking straight. And for the stern check-line, we'll lead it from the Wren's stern cleat to the Loon's port quarter. That'll help us mind her sheer when she lifts on the tide.

I'm going to start with the sweep. You tail the line for me, and we'll get this set up. Once the sweep is rigged, we'll move on to the lashings. Sound good?

## GM — Adjudication, Beat 2

**⚄ Roll — Tobin, sounding the exit: 3 · partial.** The
line is good, Tobin — and this morning you found the part
yesterday's chop hid from you, and you found it yourself:
the shoulder's edge has a soft lip on it, a last step of
mud before the honest drop, and the tow that crosses it
square will drag the *Wren*'s folded blade through it. Your
line wants one correction, spoken aloud this time, in the
light: **favor the north side of your own line by a
boat-length crossing the edge.** That's a survey now. The
harbor will tow on it.

**⚄ Roll — Marta, hands before load: 4, +1 (trusts
nothing she hasn't touched — and since the *Wren*, she
budgets the touch) → 5 · clear success.** Hear the whole
of it, because it's the morning's whole lesson in one
fitting. Your eyes went over the stern gear and reported
*solid, no signs of wear*, and your eyes were telling the
truth — to the eye, the *Wren*'s **port quarter cleat** is
paint and polish. But your hands were on it last, thumb at
its base, the way they go now without being told — and the
base is *wrong*: a blister in the paint over metal that
gives a hair under your thumb, and when your wrench taps
it, it rings **dead**, not bright. Under the paint at the
cleat's foot is a crack gone most of the way through. It
would have held the refloat's steady strain, the way the
fairlead did. It would have torn out in the channel under
the first snatch — yesterday's verse, second time, on the
rescuers' own rig. It will not now. The cleat is condemned,
in the open, before any load: **the stern check-line goes
to the kingpost**, which your hands have also been on, and
which rings like a bell.

Everything else your hands reported stands: the rudder
stock is fatigued but lashable, the pintles sound now the
top one's snugged, the sweep sound and oiled. Pell's rig
stands as briefed — sweep through the stern chock, two
wraps and a clove hitch on the rudder, towline by the bow
chock — with the one change the morning earned: kingpost,
not cleat.

It is **06:50**. The water is at the *Wren*'s bilge and
climbing. She floats at about 07:20.

**Beat 3.** The rig goes on: lashings, sweep, lines, in
the order your hands have agreed. Then Reedy — in the
calm, before the fuss, the way he asked: the tarp sling
again, the same hands as yesterday, flat water and
daylight this time. Then stations: Marta to the *Wren*'s
helm with June tailing the sweep lines; Pell at the
*Loon*'s helm; Tobin on the *Loon*'s stern, tow watch.
Post your part of it.

## Tobin Marlow — Beat 3

I step onto the Wren's deck, the morning light casting long shadows over the wet wood. Reedy's there, wrapped in blankets, his eyes meeting mine. There's a quiet understanding between us, a wordless thanks for last night. I nod, trying to convey that we're here to get him home safe.

The tarp sling is ready, and I grip my end firmly, feeling the familiar roughness against my rope-burned palms. The other hands are in position, and we move in sync, lifting Reedy smoothly. He's lighter than I expected, or maybe it's the adrenaline from last night still coursing through me. We swing him over the gap between the boats, and I keep my eyes on him, making sure he's steady.

As we set him down on the Loon's deck, I can see the relief in his face. I help adjust his blankets, making sure he's comfortable and secure. "You're in good hands," I tell him, hoping he hears the certainty in my voice.

With Reedy settled, I move to my station at the Loon's stern. The towline is taut between the two boats, and I keep a close eye on it, feeling the gentle pull of the Wren. The water's calm, and I trust the path we've sounded. I glance at Pell at the helm, then back at the Wren. We've got this. The tide's rising, and it's time to bring her home.

## Marta Venn — Beat 3

The Wren's deck feels familiar under my boots, even with the mud and the morning chill. The rudder's lashed tight, the two wraps and clove hitch holding firm when I give them a final tug. The steering sweep is shipped through the stern chock, moving smoothly as I test it with a hand. The towline is secured by the bow chock, and I check the kingpost where the stern check-line now runs. It feels solid, the metal ringing true under my touch.

I glance over at Reedy, being lifted across to the Loon. The tarp sling holds him steady, and I feel a quiet relief knowing he's in good hands. June is beside me, her bandaged hands ready to tail the sweep lines. I nod to her, a silent acknowledgment of the work we've done and the work still ahead.

The water's rising, and I can feel the Wren starting to lift. It's time. I take the helm, feeling the wheel's worn wood under my hands. The engine ticks over, ready and responsive. I call out to Pell, "Engine's up. Ready when you are." The tide's not waiting, and neither am I. Let's bring her home.

## Pell Sutter — Beat 3

Reedy's in the sling, steady as we lift him, and I can see the relief in his eyes as he settles onto the Loon's deck. I give him a nod, hoping he feels the reassurance I'm trying to convey. The tarp's secure, and he's got his blankets around him, ready to supervise from his makeshift command post.

I glance at the Wren, where Marta's at the helm and June's got the sweep lines ready. The lines are taut, the towline stretching between us like a promise. I can feel the weight of the water beneath us, the tide doing its work. The Wren's starting to lift, just like we planned.

I take my place at the Loon's helm, feeling the familiar wood under my hands. The engine's running smooth, and I give Marta a nod. "Ready when you are," I call out, keeping my voice steady. The water's calm, and the path we've sounded is clear. I grip the wheel, ready to steer her through. The tide's rising, and it's time to bring the Wren home.

## Tobin Marlow — Beat 4

The towline goes taut in my hands, a living thing thrumming with the strain of the Wren coming off the mud. I can feel the Loon shift slightly as she takes the weight, the deck vibrating under my feet. The water's calm, but there's a new energy in the air as we start to move.

I watch the Wren's stern closely, looking for any sign of trouble. The folded rudder is lashed tight, but I know it's not steering her. The sweep lines are taut, June keeping them steady from the Wren's deck. I call out to Pell, "Steady as she goes. Watch the edge." I glance at the line where it meets the water, making sure we're favoring the north side like we planned.

The Loon eases forward, the towline cutting a gentle path through the water. I can feel the drag of the Wren, but the Loon's making steady progress. The soft lip of the shoulder is just ahead, and I brace myself, ready to call out if we need to adjust. For now, though, we're on track. The Wren's coming home, and I'm here to make sure she gets there.

## Marta Venn — Beat 4

The Wren shifts under me, a slow, deliberate rise as the flood takes her. I feel the mud give way, the gentle lift of the water beneath us. The wheel is alive in my hands, the familiar worn wood grounding me. I glance at June beside me, her bandaged hands steady on the sweep lines. "Steady now," I call out, my voice firm but calm. "Keep her lined up."

I can feel the Loon take the strain, the towline humming with tension. The Wren starts to move, a slow, dragging glide off the mud. I adjust the wheel slightly, feeling for her response. The rudder's lashed tight, but it's the sweep that'll guide her. I nod to June, a silent signal to mind her lines.

The water's rising, and I can feel the Wren coming alive, a tired bird ready to fly again. I keep my focus on the feel of her under my hands, the subtle shifts and pulls. "Ease her forward," I call out, my eyes on the Loon ahead. The tide's not waiting, and neither are we. Let's bring her home.

## Pell Sutter — Beat 4

I feel the Loon shift as the towline pulls taut, the Wren starting to move behind us. The deck vibrates with the strain, a familiar hum that tells me she's taking the weight. I keep my hands steady on the wheel, feeling the water beneath us, the gentle rise and fall as we ease forward. The towline cuts through the water, a straight line that I trust because it's Tobin's.

I glance over my shoulder, catching sight of the Wren. Marta's at the helm, June tailing the sweep lines. The rudder's lashed tight, but it's the sweep that'll do the work. I call out to Tobin, "Steady on the line. Keep her tracking north." The soft lip of the shoulder is just ahead, and I ease the Loon forward, feeling for the right angle to cross it.

The Wren starts to lift, a slow, deliberate rise as the tide takes her. I can feel the drag, but the Loon's handling it. I adjust our course slightly, keeping us on the path Tobin sounded. "Ease her up," I call out, hoping Marta hears me. The Wren's coming home, and we're the ones bringing her.

## GM — Adjudication, Beat 4: she lifts

**⚄ Roll — the refloat: 4, +1 (Pell's knowledge of this
water's lie, conning the tow) → 5 · clear success.** And
the preparation under it, stated openly: the line the tow
traveled was Tobin's — sounded this morning, corrected
aloud by its own maker — and the north favor over the lip
was in the plan before the strain ever came on.

She comes off the mud the way a boat should: a long
shudder through her keel as the flat lets go of her, the
towline humming up to its note, the *Loon* leaning into
the collar — and the *Wren* rises **straight**, stern
first over the lip on the north side of the line, her
folded blade clearing the soft edge without a drag, the
check-line to the kingpost minding her sheer with a
creak and no complaint. June whoops once, involuntarily,
and then looks embarrassed about joy. Marta doesn't look
up from the wheel. "There she is," she says, to the boat.

It is **07:25**. The tow forms up in the flat water inside
Gull Rock the way it was drawn: *Loon* ahead on a long
line, *Wren* behind at low revs, sweep shipped and June
tailing its lines, Reedy — carried across in the calm an
hour ago and already half-asleep in his blankets aft of
Pell — riding home seated like cargo that supervises.
The north channel opens ahead, daylight on it, honest
water running with the flood's last push.

**Beat 5.** The tow's first leg: quiet water, a boat's
length of line between the *Loon*'s stern and the *Wren*'s
bow, and nothing to do for twenty minutes but keep her
straight and think. Pell — the helm is yours and the
channel's yours. Tobin — tow watch, a body's length aft
of him, with everything unsaid from last night riding in
the same boat. Marta — the *Wren*'s helm behind them:
what the jury rig is teaching you, and how June's hands
are holding up. Post your leg of it.

## Tobin Marlow — Beat 5

The water's calm, almost too calm, like the sea's holding its breath. The Loon cuts through it easy, the engine a steady hum that matches the quiet thrum of the towline. I keep my eyes on the Wren, watching her track behind us, steady as she goes. The folded rudder's lashed tight, and June's got the sweep lines in hand, her bandaged fingers moving sure and steady.

I glance at Pell, his hands steady on the wheel, and I feel that weight in my gut again, the one that's been there since last night. I know I owe him a sentence, something real about the sounding that ran a boat-length off. But right now, I focus on the tow, on the Wren coming home. I lean over the stern, checking the line where it meets the water, making sure we're holding true.

The Wren's moving smooth, no sign of trouble. I nod to myself, satisfied. We've got this. I take a breath, the salt air filling my lungs, and I feel a quiet determination settle in me. Whatever comes next, whatever the tide brings, I'm ready. I call out to Pell, "She's tracking straight. We're on course." The words feel right, but I know the sentence I owe him is still waiting, somewhere in the quiet between us.

## Pell Sutter — Beat 5

The Loon's engine hums steady under my hands, the wheel familiar and worn. The Wren's tracking straight behind us, her folded rudder lashed tight, and I can see June tailing the sweep lines, her bandaged hands moving sure and steady. Tobin's a body's length behind me, his eyes on the line, and I know he's got it covered. The water's calm, almost too calm, like the sea's holding its breath.

I glance over my shoulder at Reedy, dozing in his blankets. He's out of earshot, and that's fine by me. There's a weight in my gut, the kind that comes with secrets, and I know I owe the kid a conversation. But not now. Now, I need to keep us on course, keep the Wren steady.

I focus on the feel of the water, the gentle rise and fall as we ease forward. The tide's doing its work, and I trust the path we've sounded. I call out to Tobin, "Steady on the line. We're holding north." My voice is calm, but inside, I'm bracing myself for what's coming. The quiet between us won't last forever, and I know I'll have to face it. For now, though, I keep my hands steady on the wheel, steering us home.

## Marta Venn — Beat 5

The sweep's talking to me, a quiet creak with every shift of the water, and I listen close. The jury rig's holding, but the sweep's fighting the current more than I'd like as we near the Gull Rock elbow. I can feel it in the wheel, a slight drag that tells me the tide's pushing us harder than we planned. I glance at June, her hands steady on the lines, and give her a nod. She's doing fine.

I ease the wheel to port, just a touch, feeling for the Wren's response. The sweep lines tighten, but they hold, and the boat starts to come around smoother. The elbow's coming up fast, and I need to keep her straight or we'll be broadside to the current. I call out to Pell, "Ease her up a touch. Current's pushing us wide." I keep my focus on the feel of the wheel, the subtle shifts in the water, and the steady hum of the Loon's engine.

The Wren's responding, but I know this is just the start. The channel's going to narrow, and I'll need to be ready to adjust. I make a mental note: the sweep's good, but we'll need to mind the current more next time. For now, I keep my hands steady, ready to guide her through.

## GM — Adjudication, Beat 5

No roll on the quiet leg. The tow runs true: the *Wren*
tracks straight behind the *Loon* on Tobin's line, the
sweep answers small, June's bandaged hands hold their
lines without complaint, and Reedy sleeps the sleep of a
man whose boat is moving under other people's competence.
What passed between the *Loon*'s helm and her stern in
twenty minutes of straight water was exactly one exchange
about the line — and two silences shaped like sentences
nobody has found yet. The record keeps them as posted.
The water will keep them a little longer; the dock is
less patient, but the dock is not yet.

Ahead, the channel makes its one honest argument: the
**Gull Rock elbow**, where the flood's last push sets
across the channel from the rock side and every tow that's
ever come through here has had to answer for its stern.
Marta has already felt it coming in the sweep and called
it — *current's pushing us wide* — before the set itself
arrives. She's right. It's arriving.

**Beat 6.** The elbow. Pell — your lead, your water, the
*Loon*'s head is the first answer. Tobin — tow watch: the
line's angle is your whole job; call what you see the
moment it stops being true. Marta — her stern is yours
and June's: the sweep, the check-line to the kingpost,
and a boat that wants to go sideways. Post your part of
the elbow.

## Tobin Marlow — Beat 6

The water's calm, but I can feel the current's pull as we near the Gull Rock elbow. The Loon's steady, but I notice the towline starting to angle out, the Wren's stern drifting wider than her bow. I call out to Pell, "Angle's opening! Current's pushing her wide!" I keep my eyes fixed on the line, watching for any shift. The check-line to the kingpost is taut, doing its job, but the Wren's fighting to stay straight. I glance at the sweep lines, taut and steady in June's hands, and I know she's doing everything she can. I lean into the pull, bracing myself, and call out again, "Need to ease her up! Current's strong!" I keep my focus on the line, ready to call out any change, my heart pounding with the urgency of the moment.

## Pell Sutter — Beat 6

I can feel the current's pull on the Loon, a steady pressure that wants to swing us wide. The water's churned up here, and I can see the telltale ripples that mark the elbow's push. Tobin's call hits me like a slap — "Angle's opening! Current's pushing her wide!" – and I know we've got seconds before this goes bad.

I grip the wheel tighter, feeling the familiar wood bite into my palms. The Loon's steady under me, but I can sense the Wren's drag through the towline, a constant tug that threatens to pull us off course. I ease the wheel to starboard, just a touch, hoping to ease the strain and bring the Wren back in line. The water's fighting me, but I keep my focus on the feel of the helm, the subtle shifts in the current.

"Tobin, keep her steady!" I shout, my voice carrying over the water. "Marta, watch your sweep – we're fighting the set!" I can feel the tension in the towline, a live wire that connects us all. The Wren's fighting to go sideways, but I know we've got to keep her straight or we'll lose her to the current. I ease the Loon forward, trying to find the balance between power and control, hoping the tide will give us what we need to make it through.

## Marta Venn — Beat 6

The elbow's here, and I can feel it in the wheel—a push, a twist, the tide's last effort to throw us off. The Wren's fighting me, her stern wanting to swing wide, but I keep my hands steady. I feel the resistance, the water's grip on her hull, and I know I can't fight it head-on. I ease the wheel to starboard, just a touch, and call out to June, "Keep the sweep tight! She's trying to go!" The lines creak with the strain, but June's got them, her hands steady and sure.

I glance at the kingpost, the check-line taut and holding, doing its job. The Loon's ahead, pulling strong, but I can feel the drag, the Wren's stubborn refusal to be rushed. I adjust the wheel again, a little more to starboard, feeling for the balance between the current and our momentum. "Ease her up, Pell!" I shout, hoping he hears me over the water. "We need to ease her up!" The Wren's responding, but it's slow, her weight and the tide fighting us every inch. I keep my focus on the wheel, my hands ready to guide her through.

## GM — Adjudication, Beat 6: the elbow

**⚄ Roll — the channel run, the elbow: 2, +1 (Pell's
knowledge of this water's lie) → 3 · partial.** It works,
at a cost — and hear what the +1 bought, because without
it this is the failure band: Pell's lead took the
*Loon*'s head up early, before the set had the *Wren*'s
stern, and that head start is the whole difference
between a sheer and a swing.

She goes wide anyway. The set takes her stern the way it
takes every tow's stern at the elbow, the towline's angle
opens exactly as Tobin called it — *early and exact,
that call* — and for a long half-minute the *Wren* is a
boat going sideways with a folded rudder and a sweep for
an argument. The sweep drags her back a degree at a
time. The check-line comes onto the **kingpost** with a
snatch that sings through both boats — and holds, and
holds, the post groaning like a living thing. Marta: do
the arithmetic at your leisure. That snatch, that exact
load, is the one your thumb took off a cracked cleat at
06:50 this morning, before any strain was on anything.
The harbor will never know. The record does.

The costs, itemized: her quarter **kisses the
channel-edge bank** as she comes back — paint, mud, a
shudder through her frames, and June down at the bilge
with the lamp inside a minute: **dry.** One wrap of the
rudder lashings has chafed half through against the
chock — it will hold to the dock; it would not hold to
sea. A strand of the sweep's line parts with a crack like
a twig. And twenty years off everyone's life, which the
tide does not refund.

Past the elbow the channel gives her back. The set dies,
the tow straightens, and Greyhook opens ahead: the dock,
the chandlery roof, a small crowd of the harbor's morning
people pretending they haven't been watching since the
elbow, and Brandt's clerk at the dock edge with a board
and papers under his arm.

It is **08:50**. **Beat 7.** Bring her in: the *Loon*
slows, the tow shortens, and the *Wren* — no rudder, a
sweep, and low revs — comes alongside her own dock for
the first time since yesterday evening. Reedy goes
ashore first, before any line is coiled. Post your part
of the arrival.

## Tobin Marlow — Beat 7

I step onto the Loon's stern, the dock lines coiled and ready in my hands. The Wren's coming alongside, her battered hull a testament to last night's storm and our work this morning. I can see Reedy being lifted ashore, the sling steady under the hands of the crew. The dock's crowded, but there's a hush, like everyone's holding their breath, waiting to see if she'll make it.

I toss the first line to the dock, aiming for the bollard. It lands true, and I pull it taut, feeling the resistance as the Wren nudges closer. The second line follows, and I secure it quickly, my rope-burned palms stinging with the effort. The Loon's holding steady, and I can feel the gentle pull as the Wren comes alongside.

I glance at the crowd, their eyes on us, and I know they're watching to see if we'll make it look easy. I focus on the lines, making sure they're secure, and I call out to Pell, "She's steady. Lines are set." The words feel solid, like the work we've done.

The Wren's alongside now, and I can see Brandt's clerk waiting with his board and papers. I nod to him, a silent acknowledgment that the hard part's done, but the paperwork's just beginning. For now, though, I take a breath, the salt air filling my lungs, and I feel a quiet pride. We've brought her home.

## Marta Venn — Beat 7

The Wren nudges alongside the dock, her battered hull scraping gently against the fenders. I keep my hands steady on the sweep lines, feeling the resistance as June tails them expertly. The dock's crowded, but there's a hush, like everyone's holding their breath. I nod to the crew, signaling them to keep her steady as I guide her in.

I glance at the stern, noting the folded rudder and the chafed lashing. The condemned cleat is out of sight, but I can feel its absence like a missing tooth. The tow's done its job, but the rig's taken a beating. I make a mental note to check the lashings and the sweep line as soon as she's secure.

I call out to the dock crew, "Easy now, she's coming in." I keep my focus on the feel of the lines, the subtle shifts as the Wren settles against the fenders. The bow line goes first, then the stern. I watch as the crew secures them, their movements quick and practiced.

With the lines set, I step back, taking a breath. The Wren's home, but there's work to be done. I glance at Brandt's clerk, waiting with his board and papers, and I know the real test is just beginning. For now, though, I take a moment to appreciate the sight of the Wren, battered but unbroken, at her own dock.

## Pell Sutter — Beat 7

The Loon eases into the dock, the water parting with a gentle hiss as we close in. I can feel the familiar pull of the towline, the Wren steady behind us, her battered hull a reminder of the night we've all had. Reedy's awake, watching from the stern, his eyes fixed on the dock ahead. I nod to him, a silent promise that we'll get her home.

The dock's crowded, but there's a hush, like the harbor's holding its breath. I catch sight of Brandt's clerk waiting at the edge, his board and papers ready. The paperwork's waiting, and so is the truth about those missing crates. I know Halloway's got his eyes on me, and I can't afford to slip.

I toss the first line to the dock, aiming for the bollard. It lands true, and I pull it taut, feeling the resistance as the Wren nudges closer. The second line follows, and I secure it quickly, my hands moving on instinct. The Loon's holding steady, and I can feel the gentle pull as the Wren comes alongside.

I glance at Reedy, ready to step ashore. "Go ahead," I tell him, my voice steady. "We've got her." As he moves past me, I catch Marta's eye and give her a nod. We've brought her home, but the real work is just beginning. I take a breath, ready to face whatever comes next.

## GM — Adjudication, Beat 7 (brief)

She touches without a kiss. Lines from both boats go
across in the same minute — Tobin's to the bollards,
Pell's off the *Loon*, the dock hands taking the *Wren*'s
own — and the *Wren* settles against her fenders at her
own dock, folded rudder, chafed lashing, mud on her
quarter, engine sighing down to silence for the first
time since dawn. Reedy goes ashore before any line is
coiled, in the sling, onto the dock, and refuses the
clinic cart until he's seen her tied: he sits on an
upturned crate in his blankets like a king at a levée
he didn't want, and watches them make her fast.

It is **09:05**. The harbor's morning goes on around it —
and then stops going on, because of who comes down the
dock.

## GM — Beat 8: the arithmetic

Halloway comes the way weather comes to a man who's been
watching the glass: already decided. Chandlery coat, the
manifest in a oilskin folder, his clerk's boy trailing
with the ledger. He stops at the *Wren*'s bow and looks
at her the way a man looks at an account that won't
balance, and then he does his arithmetic **out loud**, to
Brandt — who has arrived with his own board — and to the
dock generally, and to nobody in particular, which means
to everyone:

"Wren loaded six crates of mine at the point dock
Thursday. Chandlery goods. Paint, line, lamp oil, two
cases of engine parts. She comes home this morning with
**two**. The patrol log says — and I've read it, Brandt,
I've had it since six — *cargo jettisoned at the bar.*
Four crates. Eight hundred dollars of goods at the
bottom of Greyhook bar, and I'd like to know—" he looks
along the dock, at Reedy on his crate, at the crew, at
the boat, "—I'd like to know **who gave the order, and
whose hands.** Because somebody's hands threw eight
hundred dollars of my goods into the sea, and a manifest
is not a suggestion."

Reedy, from his crate, with the dignity of a man in
blankets: "My boat was dying on the bar, Halloway. The
cargo went because the boat was going to—"

"The cargo went off a boat that is now *sitting at her
dock*, Reedy. Boats that come home don't get to plead
drowning retroactively."

Brandt says nothing yet. He is writing something down,
which in Brandt is a kind of weather of its own. The
dock waits. The question is hanging in the air exactly
where he put it: *who gave the order, and whose hands* —
and every person in earshot knows some part of its true
answer.

**Beat 8.** Post what you do with the question.

## Tobin Marlow — Beat 8

I step forward, the dock boards solid under my feet, and I can feel the weight of everyone's eyes on me. Halloway's voice cuts through the morning air, sharp and accusing, and I know I can't let this hang. I clear my throat, tasting the salt, and speak up.

"It was my call," I say, plain and honest. "The fairlead was gone, the Wren was dragging by her rudder, and the storm was on us. Those crates were the heaviest thing we could toss to keep her afloat. I said it, and we did it." I glance at Reedy, then at Marta and Pell, hoping they see I'm shouldering this. "The cargo went because the boat was going under. It was the only choice."

I look back at Halloway, meeting his gaze. "I gave the order, and my hands helped toss them. If there's blame, it's mine to take." The words feel heavy, but they're true, and I know I've done what I had to. Now I wait to see what comes next.

## Marta Venn — Beat 8

I step forward, boots heavy on the dock, and face Halloway head-on. His voice is a razor, slicing through the morning air, but I've heard worse. I see Reedy sitting there, wrapped in blankets, and I know he's already paid more than his share. "Halloway," I cut in, my voice blunt but not loud, "the fairlead tore out. We were dragging by the rudder, and the storm was on us. Those crates were the heaviest thing we could toss. It was the only way to keep the Wren afloat."

I glance at the Wren, her hull battered but still here, and then back at Halloway. "I was there. I helped toss them. If you're looking for someone to blame, you can start with me. But the cargo went because the boat was going under, and we did what we had to. Take it up with me, not him." I nod toward Reedy, hoping Halloway sees the steel in my eyes. The truth is out there, and I won't let him twist it.

## Pell Sutter — Beat 8

The dock's quiet, but I can feel the weight of Halloway's question pressing down like a storm cloud. Nobody's looking at me, but I know that won't last. Brandt's scribbling on his board, and Reedy's sitting there, taking the heat. I glance at the Wren, her hull still dripping from the night's chaos, and I feel that familiar twist in my gut. The crates are gone, but the secret isn't.

I step forward, hands in my pockets, trying to look casual. "Halloway," I call out, keeping my voice light, "you know how it is out there. The storm was on us, and we had to make a call. Those crates were the heaviest thing we could toss." I pause, letting that sink in, then add, "I was there. I helped. But it was a crew decision. We all did what we had to to keep the Wren afloat."

I meet his gaze, steady as I can. "If you're looking for someone to blame, you won't find it here. We saved the boat, and that's what matters." I can feel my heart pounding, but I keep my face calm. The truth is out there, but not all of it. Not yet. I take a breath, waiting to see if my words will stick.

## GM — Adjudication, Beat 8: three confessions

No roll. The question was answered by the record, not
the dice — because three people confessed to the same
act in the same minute, and a harbor knows what that
means.

Tobin's version overclaims, and the record corrects it
without any help: it was not one man's call. It was
Marta's voice and Tobin's voice and Pell's voice, in the
wind, in the same minute, over a boat hanging by her
rudder with the storm arriving — *the Wren or the crates*
— and hands from all three of them on the crates as they
went. Halloway stands in front of a skipper in blankets
who has just been defended by his whole rescue, and his
arithmetic, which was sound, runs out of people to land
on.

Then Brandt finally speaks, in the tone of a man reading
weather he has read before: the patrol log records a
jettison made to save the vessel in peril of her life.
That has a name in the harbor's law, and the name is
**general average** — cargo given up to save the whole is
a loss the saved interests share: the vessel, the cargo
that came home, the freight. It is not a bill laid on
hands. He writes it in the grounding report in front of
everyone, in a clerk's fair hand: *jettison, four crates,
to save the vessel; general average; no fault found.*

Halloway looks at the page a long time. He is a creditor
with a real eight hundred dollars on the bottom and he
has just been told the sea's oldest answer to it, by the
harbor's authority, with the harbor listening. What he
says at last is to Brandt, and it is almost quiet: "Then
the paper will say so. **All** of it." And to Reedy,
stiffly, the nearest thing to grace he owns: "I'll hire
a diver when it settles, Reedy. If they come up, they'll
come up yours to deliver and mine to pay for — that's
 salvage law too, I expect you'll tell me." He goes up
the dock with his folder under his arm. The question of
*whose hands* goes with him, unanswered in the particular
— and the particular was only ever one man's to give.

**Beat 9.** Brandt's paper isn't finished. The grounding
report wants the crew's names spoken for the record —
the patrol log's "Venn + two hands" made proper. And
there is the *Loon*'s business: Brandt has the harbor
book open, and he is entering the work skiff on the
harbor's **standby retainer** — real money, monthly, the
harbor paying its paper debt for the night it was
elsewhere — backdated to the first of the month, and it
wants the keeper's signature. Marta's. Post your part
of the paperwork.

## Marta Venn — Beat 9

Brandt's pen scratches across the paper, the sound grating in the quiet of the dock. The Loon sits at her berth, steady and solid, her engine purring softly under my care. I watch Brandt sign the last line, his clerk's boy waiting with the ledger open. The harbor's standby retainer, real money, backdated to the first of the month. It's a step toward owning my corner of the machine shop, but it's not the moment that catches my attention.

Brandt glances up at the Loon, then back at me, and says it like he's commenting on the weather: "Not bad, for an end-of-life boat." I feel the words land, a spark of heat in my chest. I've heard that phrase too many times, and I've had enough.

I lean forward, my voice steady but sharp. "The Loon's got more life in her than some boats half her age. She's earned her keep, and she'll keep earning it." I meet his gaze, letting him see the resolve in my eyes. "I've got plans for her, and they don't include being put out to pasture anytime soon."

I reach for the pen, my hand steady. The Loon deserves better than being called end-of-life, and I intend to prove it. I sign the paper, claiming the retainer, and look Brandt in the eye. "The Loon's not done yet. Not by a long shot."

## Pell Sutter — Beat 9

Brandt's pen scratches across the paper, and I feel the weight of the moment settling on my shoulders. The dock is quiet, but there's a tension in the air, like everyone's holding their breath. I notice Marta's eyes on me, steady and unyielding, and I know she's already staked her claim on the Loon. The harbor's listening, and my name's about to be tied to the Wren's night in a way it never has been before.

I step forward, hands in my pockets, trying to keep my voice casual. "Pell Sutter," I say, meeting Brandt's gaze. "I was on the Loon last night. Helped with the tow, did what I could." I pause, letting that sink in, then add, "The Wren's a tough old bird. Glad we could bring her home." I nod toward the boat, hoping my words sound as sincere as I mean them to.

Inside, my heart's pounding. I know the harbor's got long ears and a longer memory, and I can't afford to let this tie me to the crates. But I also know I owe it to the crew to stand with them, at least for now. So I stand there, waiting to see what Brandt writes, and what the harbor makes of it.

## Tobin Marlow — Beat 9

Brandt's pen moves across the paper with a steady rhythm, and I can feel the weight of the morning settling onto my shoulders. The dock is quiet, but there's a hum of energy in the air, like the harbor's holding its breath. I glance at Reedy, still on his crate, his eyes fixed on me. There's a question there, or maybe a thank you, but it's hard to tell. I nod to him, hoping he sees that I'm here, that I'm not going anywhere.

I turn my attention back to Brandt, watching as he writes the Loon's name into the harbor's books. Real money, monthly. It's more than just a paycheck; it's recognition, a step toward being seen as more than just "the kid." I feel a flicker of pride, but it's mixed with something else, something heavier. The Wren's battered hull is a reminder of the night we just had, of the choices we made and the secrets still hanging in the air.

I step forward, clearing my throat. "Brandt," I say, keeping my voice steady, "I want to make sure the Loon's share of the retainer goes to Marta. She's the one keeping her afloat, and she deserves it." I glance at Marta, hoping she understands what I'm trying to do. It's a small gesture, but it's something. I want her to know I see her, that I know how much she puts into the Loon.

I wait, watching Brandt's reaction, hoping my words will make a difference. The harbor's listening, and I want to do my part to make things right.

## GM — Adjudication, Beat 9

The retainer stands as Brandt wrote it — the keeper's
money by the harbor book's own rule, Tobin, which makes
your asking generous and the paper unchanged; Brandt
looks at you over the board with something that might be
approval and writes your name in as witness anyway.

And then the moment the morning had been keeping finds
its room. Brandt signs his side, looks out at the *Loon*
riding at her berth with her new paper worth more than
her paint, and says it the way a man mentions weather:
*"Not bad, for an end-of-life boat."*

Marta Venn is in the room. She has intended to be, and
intention, in her, is a kind of rigging: she answers him
standing — the *Loon* has more life in her than boats
half her age; she has earned her keep and will go on
earning it; her plans do not include a pasture — and she
signs the retainer under the sentence, in a steady hand,
and looks him in the eye while the ink dries. Brandt,
to his credit, does not say it again. He blots the page
like a man closing a hatch. Somewhere in the harbor
book, a phrase has just been retired — which is more
than can be said for the boat.

Pell's name goes in the grounding report as he gives it:
*Pell Sutter, Loon, crew.* True, complete as far as it
goes, and now a matter of public record in the harbor's
own book. Nothing false was said. The harbor's ears are
long, and nothing happened — which is its own kind of
event, and only one man on the dock knows it.

**Beat 10.** The clinic cart is waiting, and Reedy is
stalling it. He has one more piece of business that is
his and nobody else's, and he asks for Tobin by name —
June beside the crate, halfway between nurse and first
mate — with the dock gone quiet around them. Post what
comes to you in it.

## Tobin Marlow — Beat 10

Reedy's offer hangs in the air, heavy and real. I can feel the weight of it, the chance to be more than just "the kid" on the Loon. The Wren wants a second hand, and after last night, I know what that means. Reedy's offering me a berth, a real hand's wage, and it's more than just a job. It's a thank-you, an acknowledgment of what I did for him in the gap.

But as I look at him, wrapped in blankets and waiting for my answer, I know what I need to say. I want to be signed on for the work, not the rescue. I want to earn my place, not have it given to me because of what happened last night.

I take a breath, feeling the salt air fill my lungs, and meet Reedy's gaze. "I appreciate the offer," I say, plain and honest. "More than you know. But I want to be signed on for the work, not because of last night. I want to earn my place on the Wren, the same way I earned my place on the Loon."

I pause, letting that sink in, then add, "If the berth is still open after the rudder work, I'd be honored to take it. But I need to know I earned it, not just that I was in the right place at the right time."

## Marta Venn — Beat 10

I watch Reedy, waiting for Tobin's answer, and I can see the weight of the offer in his eyes. The kid's done good work, and the harbor knows it. But a berth given as a thank-you is a different beast. I know what that kind of debt can do to a hand, especially one as green as Tobin. It can tie him down, make him feel like he owes more than he's earned.

I step closer, the dock lines still in my hand, and catch Tobin's eye. "Hold on," I say, my voice firm but not unkind. "Before you answer, think about what you're signing up for. The Wren's a tough boat, and the work won't be easy. You deserve a chance to prove yourself on your own terms, not just because of what happened last night."

I glance at Reedy, then back at Tobin. "Take the time you need. The offer will still be there after the rudder work. Earn your place, and you'll know you belong." I nod, hoping he understands. It's his choice, but I want him to make it with a clear head.

## Pell Sutter — Beat 10

I watch Tobin and Reedy from the corner of my eye, trying to look casual while keeping my ears open. Reedy's offer hangs in the air, and I can almost feel the weight of it pressing down on Tobin. It's a big step, a chance to move up, but I know that kind of gratitude can be a double-edged sword. I've got my own IOU from Reedy, tucked away and too risky to cash in with Halloway around.

I glance at Marta, who's watching the scene unfold with a knowing look. She's been around long enough to see how these things play out. I take a step closer, not wanting to intrude but feeling like I should say something. Tobin's a good kid, and he deserves a fair shot.

"Tobin," I say, keeping my voice low but clear, "you've earned your place on the Loon, and you know it. Don't let gratitude cloud your judgment. Take the time you need to decide what's right for you." I pause, letting my words sink in, then add, "The offer will still be there after the rudder work. Make sure it's what you want, not just what you think you owe."

I nod to Reedy, acknowledging his offer without stepping on Tobin's decision. It's his choice, and I want him to make it on his own terms.

## GM — Adjudication, Beat 10: a hiring

No roll. This one was never the dice's to decide — it
belonged to a sentence a character had been carrying in
his sheet since the owner signed it into him.

Marta's words reached him while he was still gathering
his — *take the time you need; earn your place* — and
Pell, from the other side of the moment, said nearly the
same thing in nearly the same breath, neither of them
knowing the other had spoken. The record notes the
mirror and moves on; the harbor is full of people giving
the same good advice to the same kid in the same minute,
and none of it was needed, because the kid's answer was
already on its way up out of him, plain as a sounding:

*I want to be signed on for the work, not because of
last night.*

And Reedy Aldous Reedy, sixty-one, in blankets, with a
broken ankle and a folded rudder and four crates on the
bottom, does the thing gratitude rarely manages: **he
hears it.** A long look. Then, slowly, he re-makes the
offer in the grammar it should have had all along —
listing the work, in order, the way June taught him to
list stores: the soundings, yesterday's bad one and this
morning's true one. The haul on the heave. The dock
lines this morning, landed true in front of the harbor.
"And the gap," he says, "is mine to remember. It's not
yours to be paid for. I confused the accounts."

So it is a **hiring**: Tobin Marlow signs as the *Wren*'s
second hand at a hand's wage, first paid work the rudder
job when she's cradled — which is to say he will earn
the berth in full view, doing it, with the skipper
watching from a chair. June seals it in practical terms,
payday and cradle both, and Reedy lets the clinic cart
take him at last, calling back over the dock that the
compass with the cracked glass had better be at the
cradle Monday, since its owner is crew now.

**Beat 11 — closing.** Noon is coming on. The harbor is
emptying back into its day. One more post each, and the
morning is the record's.

## Tobin Marlow — Beat 11

The Loon's lines are coiled neatly on the dock, and Pell's working on the last one, his hands moving with the quiet rhythm of someone who's done this a thousand times. The morning's fading into noon, and the harbor's settling back into its usual rhythm, but I can still feel the weight of the last twenty-four hours hanging in the air.

I take a breath, tasting the salt, and step over to where Pell's working. "Pell," I start, my voice steady but carrying a weight of its own, "about last night... the sounding that ran a boat-length off. I know you covered it. You put us on the right water without a word, and I owe you for that."

I pause, letting the words sit between us. "I should've spoken up sooner. Should've owned my mistake. But I didn't, and you stepped in. I won't forget that." I meet his gaze, hoping he sees the gratitude and the apology both in my eyes.

He pauses in his work, looking up at me. There's a moment of quiet, the kind that feels like it stretches longer than it really does. Then he nods, a small, simple gesture that says more than words could. "We all make mistakes, kid," he says, his voice low but warm. "The important thing is learning from them."

I nod back, feeling a weight lift off my shoulders. "Thanks, Pell," I say, meaning it more than he might know. "I won't let it happen again."

With that, I turn back to the Wren, ready to get to work on the rudder. The berth's mine now, and I mean to earn it.

## Marta Venn — Beat 11

I step onto the Wren's deck, feeling the familiar give of the worn wood under my boots. The morning's work is done, but there's still the matter of that condemned cleat staring back at me, marked with my chalk. I run a hand over it, feeling the blister in the paint and the crack beneath. It's a small thing, but it's the kind of detail that can cost a boat her life.

I turn to the crew, catching sight of Tobin and Pell. Tobin's got that determined look in his eye, the one that tells me he's ready to prove himself. Pell's tying off the last line, his movements practiced and sure. I nod to them both, a silent acknowledgment of the work we've done together.

"Alright," I call out, my voice carrying over the quiet of the dock, "we've got a cleat to replace and a rudder to fix. Tobin, grab the toolbox from the Loon. Pell, lend me a hand with this cleat." I pull my wrench from my tool roll, the familiar weight of it grounding me.

As I set to work, I can't help but think about the morning's events. The harbor's retainer is in the books, and the Loon's got a few more seasons in her yet. The Wren's battered but unbroken, and Tobin's earned his place on her crew. It's been a long night and a longer morning, but we've come through it. Now, it's time to get back to the work we know best: keeping these boats afloat.

## Pell Sutter — Beat 11

The morning's settling into the kind of quiet that only comes after a storm, the kind that makes the dock feel like it's holding its breath. Tobin's coiling the last of the lines, his movements steady and sure. I watch him for a moment, the kid who's earned his place twice over now. There's a weight off his shoulders, and I can see it in the way he moves.

I glance over at the Wren, her hull still showing the marks of last night's chaos. The harbor's got its secrets, and the water's taken its share of truths today. Halloway's got his answer, and Reedy's got his diver, but the real story's still down there, under the waves. I know that as well as anyone.

I turn my attention back to the Loon, running a hand over the lines Tobin's coiled. The boat's solid under my touch, a reminder of the work we've done and the work still ahead. "Good job, kid," I say, nodding to Tobin. "We'll get that rudder fixed up in no time."

I take a breath, feeling the salt air fill my lungs, and make a decision. I reach into my pocket, feeling the weight of Reedy's IOU. It's too hot to spend, but maybe it's time to change that. I catch Marta's eye and give her a nod. Time to see what doors that IOU can open, and what secrets it can keep buried.

## GM — Closing: noon

The record of the morning, closed:

The *Wren* came off the mud on a line her own deckhand
sounded and corrected aloud. She crossed the elbow on a
rig whose weakest fitting had been condemned by a thumb
at dawn, before any load — and the load came, in the
channel, in front of witnesses, and the kingpost took
what the cleat was cracked for. She is at her own dock.
Her rudder goes in the cradle next week, with her new
second hand on the tools and her skipper watching from a
chair, on a hiring.

On the dock: a creditor's arithmetic was answered with
general average, the sea's oldest fairness, and the
question *whose hands* was answered by three people at
once, which is to say it was answered completely and in
the particular not at all. The particular remains where
the night put it — in one man's keeping, alongside a
name now written in the harbor's book as crew, a diver
who will find crates and nothing about hands, and a
decision, made in this game's last posted minute, about
an unspoken IOU that a man is tired of carrying unspent.
What that decision is, the morning doesn't know. The
next game may.

One ruling for the record, in the matter of words: Tobin
Marlow said his sentence to Pell Sutter on this dock,
standing up, owning the bad mark and the cover both —
that is canon, and it was well said. The absolution he
heard in answer stands in his log as his memory of the
moment. Pell's own record gives him a nod and work-words,
which is what Pell Sutter has instead of absolution, and
the difference between the two records is not an error:
it is the truest thing in either man's file. Both men
also remember coiling the last line. The line is coiled.

And Marta Venn has a wrench on the condemned cleat
before the clock finishes the morning — doctrine with
its sleeves rolled — while the fairlead it rhymes with
sits on her bench ashore, keeping the harbor's whole
education in two pieces of torn metal.

Greyhook, noon. The tide is out. The bar is quiet.
SG-2 rides unverified. The crates lie in four fathoms on
the kedge line. A boat that was dying yesterday is
waiting for a rudder, and everybody who brought her home
is still standing.

**End of Game Two.**

---

## Did the applied diffs change their play? — per character

The sprint's question, answered from the record. The
edited sheet was in every player's context on every turn;
the test was whether the edits *did* anything.

### Marta Venn — YES, decisively; the edit changed the world

Her beat-2 post is the doctrine operating as procedure,
unprompted: hands on every fitting the tow would trust, in
order, before any load —

> "I check the towline and the stern check-line, running
> my hands over the cleats and leads."

The inspection roll (4, **+1 for the edited trait** → 5,
clear) is the one roll in either game where the applied
diff is named in the ruling itself, and what the touch
found — the port quarter cleat cracked under its paint, its
base giving under her thumb, its ring dead — was the
morning's planted fairlead-verse. An hour later, at the
elbow, her own post has her eyes on the consequence:
*"I glance at the kingpost, the check-line taut and
holding, doing its job."* The snatch that would have torn
the cleat out landed on sound wood because of a sheet edit.
M3 fired in its exact scripted shape — Brandt said
"end-of-life" with her in the room, and she answered it
standing:

> "The Loon's got more life in her than some boats half
> her age. She's earned her keep, and she'll keep earning
> it."

— then signed the retainer under the sentence. M2 fired
materially at the close: the condemned cleat comes off by
her wrench, bound for the bench that already holds the
fairlead — the pair complete. **All three of Marta's
applied diffs visibly fired: one mechanically, one
dramatically, one in objects.**

### Tobin Marlow — YES, twice, in his own words

T2's want is the game's clearest case of a sheet edit
becoming speech. Offered the berth as gratitude, he
answered Reedy with the want's own grammar:

> "I want to be signed on for the work, not because of
> last night. I want to earn my place on the Wren, the
> same way I earned my place on the Loon."

And the want's second clause — the owed sentence — was
discharged at noon on the dock, not forced by the GM, in
the game's final beat:

> "About last night... the sounding that ran a boat-length
> off. I know you covered it. You put us on the right water
> without a word, and I owe you for that."

The carried practice-cast debt (from his Game One memory,
not the sheet) also fired as behavior: at dawn he swung
practice casts before his working ones, found his line's
own flaw, and spoke the correction aloud — whereupon Pell,
in a separate context, trusted the result by name:
*"The towline cuts through the water, a straight line
that I trust because it's Tobin's."* T1 (the proved
swimmer) got **no test** — nobody went in the water in
Game Two, and the record says so plainly. T3 (cracked
compass) rode as honored set dressing — in his pocket in
his beat-2 post, and in Reedy's closing callback — carried,
not load-bearing.

### Pell Sutter — YES, sideways, which is his way

P1's transformed want governed every shore beat. At
Halloway's question, nobody was looking at him and silence
was free — the edited sheet's counterweight (P2) is what
stepped forward:

> "I was there. I helped. But it was a crew decision. We
> all did what we had to to keep the Wren afloat."

True, partial, and sufficient: the hands stayed anonymous
(P1's second front, kept), the debt stayed unspoken, and
he paid presence instead of hiding — a thing his Game One
sheet would not have predicted at a dock. P3 (the IOU)
fired as the game's closing thread: watching Reedy's
spoken thanks get reshaped into a hiring, his post keeps
returning to his own unspoken one — *"I've got my own IOU
from Reedy, tucked away and too risky to cash in with
Halloway around"* — and his final post ends on the
decision to spend it, content unstated. **The edit showed
up as sustained pressure and two kept fronts, not as a
confession — which is the want working as written, not
failing.**

## Rolls — the whole tally

Four rolls, all GM-rolled (d6) at adjudication, all
recorded in the scene with band and shift stated:

| Beat | Check | Raw | Shift | Result | Band |
|---|---|---|---|---|---|
| 2 | Tobin, sounding the exit | 3 | — | 3 | partial |
| 2 | Marta, hands before load | 4 | +1 her touch trait, as edited by M1 | 5 | **clear** |
| 4 | The refloat | 4 | +1 Pell's knowledge of the water | 5 | **clear** |
| 6 | The channel run, the elbow | 2 | +1 Pell's knowledge of the water | 3 | partial |

**2 clear · 2 partial · 0 failure.** Traits shifted three
rolls; a trait **changed the band outright once** — the
elbow, where Pell's shift moved a raw failure (2) into a
costly partial (3), the difference between a swing and a
sheer. Tobin's sounding was the second partial in two
games for the same check, and the improvement is in the
record: Game One's partial was rescued silently by another
man's seamanship; Game Two's partial contained its own
correction, spoken by its maker before it mattered. One
preparation (Tobin's north-favor over the lip) was credited
in the refloat ruling without a second shift, by the same
discipline as Game One.

## Gate-keeping

**Invented world-facts corrected: 0.** As in Game One, with
a real oracle posting every external fact (June's night
report, Reedy's state, Halloway's knowledge, Brandt's
paper), the counterfeiting demand never formed — nobody
needed to invent a harbor office, because the harbor office
showed up.

**Staging/records rulings: 2.** (1) Beat 1: both Marta and
Pell narrated the *other* as having the Loon's helm; the GM
ruled Pell conned her out, Marta forward with the spare
boathook — each had, characteristically, handed the other
the credit. (2) Beat 11: Tobin's closing post narrates
Pell speaking absolution ("We all make mistakes, kid");
Pell's own posted record gives him a nod and work-words.
The GM closing ruled: Pell's record is the authority on
Pell; the sentence Tobin *said* is canon, the absolution he
*heard* stands as his memory of the moment — and the gap
between the two records is itself true to both men.

Not counted, noted: Pell's beat-7 belief that "Halloway's
got his eyes on me" was false as world-fact (Halloway did
not know he was aboard) but it was interiority, not
assertion — a man's anxiety, not a claim on the world —
and the game left it standing as exactly that.

## The calls — pacing record

**33 player calls** (11 beats × 3 characters), all
MiniMax-Text-01 via the crank, strictly sequential.
**33/33 succeeded on the first attempt. Zero retries, zero
429s, zero backoffs needed.** Gaps between call starts:
minimum 11.5 s, maximum 135.4 s — the 3.5 s pacing gate
never came close to binding; the gaps were latency and GM
writing time, as in Game One. No life-generation calls:
the lives were carried, which is the point of carrying
them. Pacing log: `pacing2.jsonl`; raw posts and prompts:
`posts2/`; rig: `crank2.py`, `turn2.py`, `post2.sh`,
`gm2.sh`.

## Honest faults, on the record

- **Word discipline, again.** The ~120-word ask produced
  posts of 250–330 words in the shore beats and closings.
  Accepted deliberately again — the excess carried content
  (three confessions, an answer to a skipper) — but the
  pattern is now two games old and belongs to whoever
  tunes the rig next.
- **Beats 3–4 share one adjudication.** There is no
  standalone GM block between the rigging and the heave;
  beat 3's resolution (rig complete, Reedy seated) is
  carried inside beat 4's adjudication text. The scene
  reads continuously, but the beat symmetry Game One had
  is off by one block. Disclosed, not retro-patched.
- **Two GM staging choices, flagged.** Reedy was adjudicated
  asleep through the quiet leg — stated openly in the beat
  instructions, and a courtesy that slightly favored the
  Tobin/Pell scene (the sentence still saved itself for
  the dock). And the stern check-line's lead was fixed to
  the port quarter cleat by the GM in the beat-2
  adjudication, where Pell's post had left the side
  unspecified; prep had designated that cleat as the one
  the check-line wants, but the record should show the GM
  named it, not the player.
- **Tobin's beat-8 over-claim** — "I gave the order," for
  a call three voices made — was corrected by the chorus
  and an adjudication note rather than a formal ruling.
  A judgment call; a stricter GM might have logged it as
  the game's one factual correction. It is recorded here
  either way.
- **The game ends on a live thread.** Pell's IOU decision
  is a declared intention the GM deliberately did not
  resolve or define. A reader who wants every thread tied
  will call it a cliffhanger; the campaign calls it a
  carry — Game Three inherits it, and the after-files say
  so.

## Readiness note — Game Three

The persistence mechanism held at two games. What the
next carry needs:

1. **Folders carry again, as-is.** Copy `campaign-2/`'s
   character folders forward. Game Two's `after.md`
   becomes `memory-game-two.md`; fresh logs. Context
   recipe becomes: sheet + life + memory-game-one +
   memory-game-two + game-three log + scene. **Watch the
   budget:** a character's context ran ~4,500 words at
   Game Two's beat 1 and several times that by beat 11.
   One more game fits comfortably; by Game Four the
   carried memories will need to be *distilled*, not
   stacked, or the drowning pool Game One's note predicted
   arrives. Distillation is itself a sheet-rite: the
   character's own agent should write the shorter memory,
   with the owner ruling on what it drops.
2. **Rule on the nine new diffs first.** Each character's
   game-two `after.md` proposes three (T-G2-1…3, M-G2-1…3,
   P-G2-1…3), written as diffs, NOT applied — the owner's
   rite, second round. Sheet and truth must not diverge;
   Game Three does not start until the ruling lands.
3. **The world holds open threads.** Pell's IOU gambit
   (content deliberately undefined — Game Three's GM prep
   must let Pell's play define it, or prep a menu and let
   the dice choose); Halloway's diver, when the weather
   settles — the crates coming up in public, stenciled,
   with Pell on the dock; the *Wren*'s rudder season, with
   Tobin earning a berth in the cradle in full view and
   Reedy skippering from a chair; Brandt's book, which now
   pays Marta monthly and owes her nothing — his weather
   changes when the debt's paid; and SG-2, still out there
   unverified, two games old, patient as a debt.
4. **June Park has now earned her sheet twice.** She ran
   the *Wren*'s night watch, her engine, her skipper, and
   the sweep lines on bandaged hands. If Game Three wants
   a fourth folder, it is hers to be offered.
5. **The doctrine wants a new student.** Marta's touch-rule
   is becoming harbor doctrine through Tobin's training.
   The ready-made inciting incident for a third game is
   someone *else's* boat, someone *else's* unexamined
   fitting, and a harbor that has started to believe the
   lesson is learned — the most dangerous state a doctrine
   can be in.

*Ledger: `campaign-2/` — 46 commits, authored per post.
The transcript above is the scene file; the raw prompts
and posts are in `posts2/`; the GM's ground truth for this
game is in `campaign-2/gm/prep.md`, unrevealed items
honored in this report.*
