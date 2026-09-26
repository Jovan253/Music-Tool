## 1. Design foundation

- [x] 1.1 Replace `index.css` boilerplate with console tokens, fader, panel and legend treatments
- [x] 1.2 Delete `App.css` and the unreferenced template assets

## 2. Mixer

- [x] 2.1 Rebuild `TrackRow` as a channel strip with colour marker, lit solo/mute and a fader readout
- [x] 2.2 Add a transport bar with play/pause, ±5s skip and a position/duration readout
- [x] 2.3 Dim channels silenced by another channel's solo
- [x] 2.4 Colour each waveform by channel and add an audio-shaped loading skeleton
- [x] 2.5 Surface a stem-loading failure instead of rendering an empty console

## 3. Other screens

- [x] 3.1 Restyle upload, including a progress bar with ARIA roles and a real error surface
- [x] 3.2 Restyle login and the post-signup confirmation screen
- [x] 3.3 Restyle export controls into the transport bar

## 4. Responsive

- [x] 4.1 Stack channel rows on narrow viewports
- [ ] 4.2 Verify on a real phone viewport

## 5. Verify

- [x] 5.1 Build and lint clean
- [x] 5.2 Visually confirm the login screen
- [ ] 5.3 Visually confirm the mixer — needs an authenticated session or the public demo page
