## Why

The app worked but looked like an unstyled prototype, which matters because it is a portfolio piece: the interface is the first and often only thing a visitor judges.

Two concrete causes, beyond taste. `src/index.css` was still Vite template boilerplate — it pinned `#root` to a fixed 1126px box with side borders, centred all text, set `h1` to 56px with negative letter-spacing, and declared a **light** colour palette that every dark Tailwind class then had to fight. `src/App.css` was a further 184 lines of template CSS (`.counter`, `.hero`, `.vite`) that nothing imported at all.

The mixer also under-sold what it does. It presented four sliders in a list; it is a four-channel console, and it should look like one.

## What Changes

- Replace `index.css` with a studio design-token layer: console greys, one hue per channel, a fader treatment, a recessed-panel treatment, and a mono "legend" style for hardware-style labels
- Rebuild the mixer as a channel strip — colour-coded channel, waveform, lit solo/mute, fader with a numeric readout — plus a transport bar with play, ±5s skip, and a time readout that did not exist before
- Waveforms take their channel's colour and show an audio-shaped loading skeleton instead of a text placeholder
- Restyle upload, login and export to match; add real error surfaces and a progress bar with proper ARIA
- Make every screen work on a phone: channel rows stack rather than overflow
- Delete `App.css` and three unreferenced template assets

Committed to a single dark theme rather than supporting both. Mixing hardware is dark, and a light variant of this would read as a generic web form.

## Capabilities

### Modified Capabilities

- `stem-mixer`: the mixer gains a transport with a time readout and seek controls, per-channel visual identity, loading and error states, and a mobile layout

## Impact

- `apps/web/src/index.css` — rewritten
- `apps/web/src/features/mixer/` — `StemMixer`, `TrackRow`, new `stemColors.ts`
- `apps/web/src/features/waveform/Waveform.tsx` — colour and skeleton. The effect's narrow deps and `active` guard are preserved deliberately: three prior commits fixed StrictMode races there
- `apps/web/src/features/upload/UploadZone.tsx`, `features/auth/LoginPage.tsx`, `features/export/ExportButton.tsx`
- Deleted: `App.css`, `assets/react.svg`, `assets/vite.svg`, `assets/hero.png`
- No API, schema or behaviour changes
