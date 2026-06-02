## ADDED Requirements

### Requirement: Fullscreen Toggle Option
The system SHALL display a magnifying glass icon button (zoom-in icon) near the top-right corner of the active CAD viewer component card. Clicking this button SHALL trigger a maximized fullscreen view of the CAD drawing.

#### Scenario: User clicks the magnifying glass button
- **WHEN** the user clicks the magnifying glass button on an active CAD viewer preview card
- **THEN** the system SHALL hide the standard designs list layout and render the maximized CAD viewer workspace in the main content area

### Requirement: Fullscreen CAD Rendering
The maximized CAD view SHALL occupy the main content area next to the Copilot sidebar. It SHALL render the active design's CAD drawing using the DXF content associated with the active design without triggering any additional DXF generation requests or file uploads.

#### Scenario: Fullscreen viewer displays active CAD drawing
- **WHEN** the user enters fullscreen mode for a design entry
- **THEN** the system SHALL load the design's DXF content and scale the CAD viewer canvas to fit the dimensions of the maximized container

### Requirement: Exit Fullscreen Mode
The system SHALL display a back button in the header of the maximized CAD view. Clicking this button SHALL exit fullscreen mode and return the user to the standard designs list.

#### Scenario: User clicks back button to exit fullscreen
- **WHEN** the user clicks the back button in the maximized CAD view header
- **THEN** the system SHALL close the maximized workspace and restore the standard designs list layout

### Requirement: Fullscreen Translation
The fullscreen header title and back button SHALL support both English and Slovak languages based on the active locale.

#### Scenario: User switches language in fullscreen mode
- **WHEN** the user toggles the active language to Slovak
- **THEN** the fullscreen header title and back button SHALL be rendered in Slovak translation
