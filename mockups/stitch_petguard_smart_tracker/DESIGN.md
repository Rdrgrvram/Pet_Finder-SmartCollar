---
name: Kinetic Paws
colors:
  surface: '#f8f9ff'
  surface-dim: '#ccdbf3'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e6eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d5e3fc'
  on-surface: '#0d1c2e'
  on-surface-variant: '#424656'
  inverse-surface: '#233144'
  inverse-on-surface: '#eaf1ff'
  outline: '#727687'
  outline-variant: '#c2c6d8'
  surface-tint: '#0054d6'
  primary: '#0050cb'
  on-primary: '#ffffff'
  primary-container: '#0066ff'
  on-primary-container: '#f8f7ff'
  inverse-primary: '#b3c5ff'
  secondary: '#006e1c'
  on-secondary: '#ffffff'
  secondary-container: '#91f78e'
  on-secondary-container: '#00731e'
  tertiary: '#565a5b'
  on-tertiary: '#ffffff'
  tertiary-container: '#6f7274'
  on-tertiary-container: '#f6f8fa'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae1ff'
  primary-fixed-dim: '#b3c5ff'
  on-primary-fixed: '#001849'
  on-primary-fixed-variant: '#003fa4'
  secondary-fixed: '#94f990'
  secondary-fixed-dim: '#78dc77'
  on-secondary-fixed: '#002204'
  on-secondary-fixed-variant: '#005313'
  tertiary-fixed: '#e0e3e5'
  tertiary-fixed-dim: '#c4c7c9'
  on-tertiary-fixed: '#191c1e'
  on-tertiary-fixed-variant: '#444749'
  background: '#f8f9ff'
  on-background: '#0d1c2e'
  surface-variant: '#d5e3fc'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  stat-display:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.03em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
  card-padding: 24px
---

## Brand & Style
The design system focuses on the intersection of high-technology and the warmth of pet ownership. It targets modern pet owners who value data-driven insights but require an interface that feels approachable and stress-free. 

The visual style is **Modern Minimalist** with a **Tactile** edge. It employs a clean, card-based architecture that organizes complex biometric data into digestible modules. The interface should evoke a sense of "calm intelligence"—reliable enough for health monitoring, yet friendly enough for daily interaction. High whitespace, soft transitions, and intentional use of color for connectivity status define the aesthetic.

## Colors
The palette is anchored by **Tech Blue**, used exclusively for primary actions and "Connected" states, signaling reliability. **Sage Green** serves as the "Health & Vitality" accent, used for activity goals, battery status, and positive growth metrics. 

**Slate Greys** provide the structural foundation:
- **Surface:** #F8FAFC (Ultra-light tint for background)
- **Border:** #E2E8F0 (Subtle separation)
- **Text Primary:** #1E293B (Deep slate for maximum legibility)
- **Text Secondary:** #64748B (Muted slate for metadata)

The background uses a subtle gradient from the primary blue (2% opacity) to white to soften the workspace.

## Typography
This design system utilizes **Inter** for its systematic clarity and neutral tone. The scale is designed to handle dense data (like GPS coordinates or heart rate logs) without feeling cluttered.

- **Headlines:** Use tight letter-spacing and bold weights to ground the cards.
- **Stats:** A dedicated `stat-display` role is used for key metrics (e.g., "Step Count" or "Calories") to create immediate visual impact.
- **Labels:** Uppercase labels are used for small metadata to differentiate them from actionable body text.

## Layout & Spacing
The layout uses a **Fluid Grid** based on an 8px rhythm. Content is housed in a central container that maxes out at 1280px to ensure data visualizations don't become overly stretched on ultra-wide monitors.

- **Desktop:** 12-column grid with 24px gutters. Use 3-column or 4-column spans for data cards.
- **Tablet:** 6-column grid. Sidebars collapse into a bottom navigation bar or a hamburger menu.
- **Mobile:** Single column with 16px side margins. Cards stack vertically.
- **Spacing Philosophy:** Priority is given to negative space around cards to prevent the "dashboard fatigue" common in technical apps.

## Elevation & Depth
This design system uses **Tonal Layering** combined with **Ambient Shadows** to create a soft, accessible depth. 

- **Level 0 (Background):** #F8FAFC.
- **Level 1 (Cards):** White (#FFFFFF) with a very soft, diffused shadow: `0px 4px 20px rgba(0, 0, 0, 0.05)`.
- **Level 2 (Interaction):** On hover, cards lift slightly with a more pronounced shadow: `0px 10px 30px rgba(0, 0, 0, 0.08)`.
- **Overlays:** Modals and dropdowns use a "Glass" effect with a 12px backdrop-blur and a 1px white border at 50% opacity to mimic a high-end physical device.

## Shapes
The shape language is defined by a **Large Radius** approach to maximize "friendliness." 

- **Primary Radius:** 0.5rem (8px) for input fields and small buttons.
- **Card Radius (rounded-lg):** 1rem (16px) for the primary dashboard modules.
- **Feature Radius (rounded-xl):** 1.5rem (24px) for large hero sections or pet profile containers.
- **Status Indicators:** Fully rounded (pill-shaped) for tags and connectivity icons.

## Components
- **Buttons:** Primary buttons use a solid Tech Blue fill with white text. They are large (min-height 48px) with rounded-lg corners. Secondary buttons use a Sage Green outline.
- **Cards:** The core of the UI. Every card must have a 24px internal padding. Content inside should be grouped logically with a 12px gap.
- **Status Chips:** Small, pill-shaped badges. "Active" uses a Sage Green background at 10% opacity with solid Green text. "Syncing" uses Tech Blue.
- **Inputs:** Clean white fields with a 1px Slate-200 border. Focus state switches the border to Tech Blue with a 2px outer glow.
- **Data Visualizations:** Line charts should use a thick (3px) stroke in Tech Blue with a soft gradient fill beneath the line. Avoid sharp corners on graph lines; use smoothed "catmull-rom" curves.
- **Pet Profile Switcher:** A circular avatar component with a 2px Tech Blue border ring to indicate which pet's data is currently being viewed.