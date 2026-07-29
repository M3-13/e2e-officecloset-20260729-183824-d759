# Design — Project Identity

> This document is project-long-lived. Tokens are not changed without
> the Architect's approval. Developers MUST use these tokens
> instead of improvising their own colors/spacings.

## Style Direction

Tiefes Anthrazit-Schwarz mit warmem Champagner-Gold als Akzent, getragen von einer eleganten Serifenschrift und sanften Spiegel-Glow-Effekten – das digitale Äquivalent eines begehbaren Kleiderschrankes mit Samtdetails, gedimmten Kristallleuchtern und raumhohen Spiegeln.

## Colors

- `--color-bg`: **#141211**
- `--color-fg`: **#F5F0EB**
- `--color-accent`: **#C9A84C**
- `--color-accent-hover`: **#D9BC62**
- `--color-accent-muted`: **#A68A3C**
- `--color-surface`: **#1E1B1A**
- `--color-surface-elevated`: **#292524**
- `--color-border`: **#3D3835**
- `--color-border-light`: **#524C48**
- `--color-muted`: **#A39A92**
- `--color-error`: **#C95B4A**
- `--color-success`: **#7B9E6B**
- `--color-glow`: **rgba(201, 168, 76, 0.18)**
- `--color-samtschwarz`: **#0D0B0A**

## Typography

- `font_family`: 'Playfair Display', 'Cormorant Garamond', Georgia, 'Times New Roman', serif
- `heading_weight`: 600
- `body_weight`: 400
- `body_font_family`: 'Lato', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif
- `size_scale`: xs: 0.75rem; sm: 0.875rem; base: 1rem; lg: 1.125rem; xl: 1.375rem; 2xl: 1.75rem; 3xl: 2.25rem; 4xl: 3rem

## Spacing Scale

- `--space-0`: 4px
- `--space-1`: 8px
- `--space-2`: 12px
- `--space-3`: 16px
- `--space-4`: 24px
- `--space-5`: 32px
- `--space-6`: 48px
- `--space-7`: 64px
- `--space-8`: 96px

## Border-Radii

- `--radius-sm`: 4px
- `--radius-md`: 8px
- `--radius-lg`: 16px
- `--radius-xl`: 24px
- `--radius-pill`: 999px

## Components

### Button (Primary)

padding 12px 28px, radius md, bg=accent, color=#141211, font-weight 600, font-family serif, letter-spacing 0.04em, border none, min-height 48px, cursor pointer. Hover: bg=accent-hover, box-shadow 0 0 20px glow, transform scale(1.03), transition all 0.25s ease-out. Active: transform scale(0.97), transition 0.1s. Disabled: opacity 0.45, cursor not-allowed, no shadow. Focus-visible: outline 2px solid accent, outline-offset 3px.

### Button (Secondary)

padding 12px 28px, radius md, bg=transparent, color=accent, border 1.5px solid accent, font-weight 600, font-family serif, letter-spacing 0.04em, min-height 48px, cursor pointer. Hover: bg=glow, border-color=accent-hover, color=accent-hover, box-shadow 0 0 14px glow, transform scale(1.03), transition all 0.25s. Active: scale(0.97). Disabled: opacity 0.4.

### Button (Danger/Ghost)

padding 10px 24px, radius md, bg=transparent, color=error, border none, font-family sans-serif, font-weight 500, min-height 44px, cursor pointer. Hover: bg=rgba(201,91,74,0.1), transition all 0.2s. Disabled: opacity 0.4.

### Text Input

padding 12px 16px, radius md, bg=surface, color=fg, border 1.5px solid border, font-family sans-serif, font-size base, min-height 48px, width 100%, caret-color accent. Placeholder: color=muted, font-style italic. Focus: border-color=accent, box-shadow 0 0 0 3px glow, outline none, transition border 0.2s, box-shadow 0.2s. Error: border-color=error. Disabled: opacity 0.5, bg=#1A1817.

### Card (Kleidungsstück / Outfit)

bg=surface, radius=lg, border 1px solid border, padding 16px, overflow hidden, transition all 0.3s ease. Hover: border-color=border-light, box-shadow 0 8px 28px rgba(0,0,0,0.45), transform translateY(-2px). Image wrapper: aspect-ratio 3/4, bg=#0D0B0A, radius=md inside card. Title: font-family serif, font-size lg, color=fg, margin-top 12px. Meta: font-family sans-serif, font-size sm, color=muted.

### Navigation Bar

sticky top, bg=rgba(20,18,17,0.92), backdrop-filter blur(18px), border-bottom 1px solid border, padding 16px 32px, display flex, align-items center, justify-content space-between, z-index 50. Logo/Brand: font-family serif, font-size xl, font-weight 600, color=accent, letter-spacing 0.06em. Nav Links: display flex, gap 32px, font-family sans-serif, font-size base, color=muted. Nav Link hover: color=fg, transition color 0.2s. Active link: color=accent, underline effect via border-bottom 2px solid accent.

### Modal / Dialog

overlay: bg=rgba(0,0,0,0.65), backdrop-filter blur(4px), position fixed, inset 0, z-index 100. Panel: bg=surface-elevated, radius=lg, border 1px solid border, padding 32px, max-width 520px, width 90vw, position centered, box-shadow 0 24px 64px rgba(0,0,0,0.6), animation fadeIn 0.25s ease. Title: font-family serif, font-size 2xl, color=fg, margin-bottom 24px. Close icon: absolute top 16px right 16px, color=muted, hover color=fg.

### Category Filter Tabs

display flex, gap 8px, overflow-x auto, padding 4px 0. Tab: padding 8px 20px, radius=pill, bg=transparent, color=muted, font-family sans-serif, font-size sm, font-weight 500, border 1px solid transparent, cursor pointer, white-space nowrap, min-height 40px, transition all 0.2s. Hover: color=fg, border-color=border-light. Active: bg=accent, color=#141211, border-color=accent, font-weight 600.

### Image Upload Zone

dashed border 2px dashed border, radius=lg, bg=surface, padding 48px 24px, text-align center, cursor pointer, min-height 200px, display flex, flex-direction column, align-items center, justify-content center, gap 12px, transition all 0.25s. Icon: color=muted, font-size 2.5rem. Text: font-family sans-serif, color=muted, font-size sm. Hover: border-color=accent, bg=rgba(201,168,76,0.04), box-shadow inset 0 0 40px glow. Drag-active: border-color=accent-hover, bg=rgba(201,168,76,0.08). Preview: img fills zone, radius=md, object-fit cover.

### Outfit Canvas / Creator

bg=surface, radius=lg, border 1px solid border, padding 24px, display grid, grid-template-columns repeat(auto-fit, minmax(140px,1fr)), gap 16px, min-height 320px. Empty state: display flex, flex-direction column, align-items center, justify-content center, color=muted, font-family sans-serif, icon 3rem, text 'Ziehe Teile hierher oder wähle aus'. Slot: aspect-ratio 3/4, bg=samtschwarz, radius=md, border 2px dashed border, transition all 0.2s. Slot filled: border solid border-light, img covers. Slot hover empty: border-color=accent, bg=rgba(201,168,76,0.05).

### Toast / Notification

position fixed, bottom 24px, right 24px, z-index 200, padding 14px 22px, radius=md, bg=surface-elevated, border 1px solid border, box-shadow 0 8px 24px rgba(0,0,0,0.5), font-family sans-serif, font-size sm, color=fg, display flex, align-items center, gap 10px, animation slideUp 0.3s ease. Success variant: border-left 3px solid success. Error variant: border-left 3px solid error. Info variant: border-left 3px solid accent.

## Layout Principles

- Maximale Inhaltsbreite 1280px, zentriert mit horizontalem Padding von 24px (Mobile: 16px)
- Breakpoints: Mobile < 640px, Tablet 640–1024px, Desktop > 1024px. Garderoben-Grid: 2 Spalten Mobile, 3 Spalten Tablet, 4 Spalten Desktop
- Vertikaler Rhythmus: Sektionsabstand 48px (Mobile: 32px), Kartenabstand 24px (Mobile: 16px). Page-Wrapper padding-top 32px unter der NavBar
- Gold-Glow-Akzente sparsam einsetzen: nur bei Primär-Buttons, fokussierten Inputs und Hover-Effekten – nie flächig. Die Eleganz lebt vom Kontrast zwischen Dunkel und punktuellem Licht
- Animationen: alle Übergänge 0.2–0.3s ease-out, keine springenden Bewegungen. Seitenwechsel mit sanftem Fade (opacity + translateY 6px, 0.25s). Das fühlt sich an wie ein Licht, das langsam angeht – kein greller Schnitt
- Schatten sind weich und warm (schwarz mit leichter Rot-Braun-Beimischung), nie hart. Card-Shadow: 0 4px 20px rgba(0,0,0,0.4). Elevated-Shadow: 0 12px 40px rgba(0,0,0,0.55)
- Leerraum ist ein Stilmittel: großzügige Abstände zwischen Sektionen lassen die Oberfläche atmen und vermitteln Exklusivität. Nichts drängeln, nichts quetschen
