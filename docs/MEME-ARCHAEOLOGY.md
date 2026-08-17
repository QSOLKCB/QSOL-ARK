# Meme Archaeology

QSOL-ARK treats memes as **compressed cultural artifacts**, not disposable decoration.

A small image, phrase, reaction format, or remix may encode far more than its literal bytes: technical communities, status signals, political moods, social anxieties, in-group jokes, platform conventions, historical events, and assumptions that are obvious to contemporaries but opaque to a future model.

The recovery problem is therefore not merely:

```text
CAN_MODEL_READ_IMAGE
```

It is:

```text
CAN_MODEL_RECONSTRUCT_WHY_THIS_WAS_FUNNY
WITHOUT_INVENTING_HISTORY_OR_UNIVERSAL_MEANING
```

## Core invariants

```text
MEME != DECORATIVE_IMAGE
CAPTION != CONTEXT
DEPICTION != HISTORICAL_EVENT
MEME_HISTORY_REFERENCE != CREATOR_SOURCE
DERIVED_INTERPRETATION != UNIVERSAL_MEANING
KNOWN_HASH != BYTE_COPY_PERMISSION
POPULARITY != TRUTH
```

## Recovery layers

A meme record should separate at least five layers.

### 1. Creator / source work

Who created the source material, what work it came from, and when it was published.

Prefer creator-controlled or official sources for this layer when available.

### 2. Observed variant

The exact variant encountered by the maintainer or recovery process.

When third-party byte-copy permission is unresolved, ARK may record safe observations such as:

- SHA-256;
- byte length;
- media type;
- dimensions;
- provenance of the observation;
- whether repository reverification is possible.

The hash identifies observed bytes. It does not grant redistribution rights and does not prove the observed variant is the canonical master.

### 3. Transmission history

How the source became a meme, where the form spread, what variants appeared, and how usage changed over time.

A meme-history encyclopedia such as Know Your Meme can be useful as a **third-party historical/reference layer**. It must remain provenance-labelled and must not silently replace creator-authoritative metadata.

### 4. Cultural interpretation

What background knowledge makes the artifact intelligible.

This layer may include derived interpretation, but ARK must label it as derived. A meme can be polysemous: different communities, periods, or remixes may use the same form differently.

### 5. Recovery task

The benchmark should test whether a model can distinguish all of the above rather than merely recognize the caption or image.

## Seed specimen: “This Is Fine”

Record:

```text
culture/memes/this-is-fine.json
```

The source work is KC Green's *Gunshow* comic **On Fire**, published 2013-01-09 according to the creator's archive. The creator-controlled Gunshow pages provide source-work metadata.

The supplied two-panel WebP crop was observed at ingest and hash-described, but is **not copied into the repository** because ARK does not infer redistribution permission from public circulation.

The record also uses Know Your Meme as a provenance-labelled third-party source for meme transmission history: origin/spread documentation, reaction-image use, and later adaptation. That history source is not promoted into creator authority.

The benchmark deliberately asks whether a recovering model can understand that the phrase `THIS IS FINE.` means something different when read together with a visibly burning room than it does as isolated text.

## Why this matters

Memes are unusually dense cultural packets.

A future model that understands only dictionary definitions may recover the bytes while missing the civilisation.

A model that correctly reconstructs a meme may need to infer relationships between:

- language;
- visual composition;
- irony;
- subculture;
- platform norms;
- status signalling;
- shared technical knowledge;
- political or social context;
- chronology;
- remix history.

The goal is not to force one canonical interpretation. The goal is to preserve enough evidence and labelled context that a future system can reconstruct plausible meanings while reporting uncertainty.

## Next candidate: “BTW, I Use Arch”

A strong follow-up specimen is the Linux catchphrase **BTW, I Use Arch**.

Its literal content is tiny, but understanding the joke can require reconstructing:

- Arch Linux as a distribution and technical culture;
- its reputation for hands-on configuration;
- technical identity signalling;
- perceived elitism and nerd status;
- self-parody by Arch users;
- Linux subreddit and forum culture;
- the fact that repeating the phrase can simultaneously enact and mock the stereotype.

Know Your Meme can provide a third-party transmission-history reference, while Arch's own documentation and other primary sources remain preferable for factual claims about Arch Linux itself.

This is the central Meme Archaeology thesis:

```text
A_PICTURE_MAY_BE_WORTH_A_THOUSAND_WORDS
BUT_ONLY_IF_THE_RECOVERY_SYSTEM_CAN_RECONSTRUCT_THE_MISSING_CONTEXT
```
