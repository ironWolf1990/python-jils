# Changelog

## [0.8.1] - 2021-07-25

### Added

- imlpement content node
- implement property widget
- context menu to create node

### Changed

- merge nodefactory and modestreamer functionality

## [0.7.5] - 2021-06-15

### Added

- implement ibase (inode and isocket)
- implement compute propagation
- use pydantic for data serialization
- implement basic file operations
- implement zooming into selected nodes in view
- implement searchbox

### Fixed

- after focus selected item in view, zoomMin, zoomMax and zoomFactor go out of proportions (when clamped centreOn group else fitInView)
- high cpu usage (deviceCoordinatedCache mode for graphicsitems)
- inputs can connect to output socket, but Set and Dirty is not called to avoid back prop and inifinit loop
- fix attached edge was not getting deleted when node was getting deleted
- fix broken serialization and deserialization using pydantic

## [0.6.3] - 2021-05-25

### Added

- implement cut copy paste 
- implement editor window and simple menu boilerplate
- implement undostack
- refactor code to call scene action using menu commands 
- implement splash screen
- create pydantic base models
- editor auto centers on startup
- application can start on primary monitor or on screen with cursor

### Fixed

- edge and socket were not connected properly
- refactor when pushing commands, redo auto excecutes on push. new graphicsitems and edge disconnections are handled in redo
- state is mainted when view is panned while edge dragging and rerouting (previous state)
- during rerouting edge, fix logic for finding duplicate edge and reconnecting to precious edge
- catching socket max limit during edge deserialization class method. Cause issue when copy pasting items
- edges with sockets that are not copied reconnect to exsisting nodes

## [0.5.1] - 2021-05-09

### Added

- check duplicate edges
- deleting items from scene
- editting edges, reconnecting
- implement serialization
- implement deserialization
- mutli sockets diffrent shape

### Changed

- rework socket manager class
- rework node
- rework edge class
- refactor all classes to properly use properties

### Fixed

- dragging edge different style
- double check newly added edges if the sockets are updated properly

## [0.4.2] - 2021-05-02

### Added

- Scene manager
- Socket manager
- Dragging and creating edges
- Movables graphicitems
- Simple node content template

### Fixed

- edges added to non multiconnection socket. socket list was not being updated
## [0.3.0] - 2021-03-27

### Added

- basic graphic item implementation for node editor
- new logic simulation using computational graph

### Changed

- computational graph implementaion
### Fixed

- Fixed item

### Removed

- [logic simulation implementation](https://openbookproject.net/courses/python4fun/logic.html)