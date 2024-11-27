# Changelog

## [v1.2.0] - 2024-11-27
### Added
- **Mining Devices**: Introduced new mining devices with balanced prices and mining rates.
  - AXIS-X01 (Free, 1-3 coins)
  - AXIS-X02 (250$, 2-4 coins)
  - AXIS-X03 (500$, 3-6 coins)
  - AXIS-X04 (1000$, 5-8 coins)
  - AXIS-X05 (2500$, 7-12 coins)
  - AXIS-X06 (4000$, 9-15 coins)
  - AXIS-X07 (6500$, 12-18 coins)
  - AXIS-X08 (10000$, 15-25 coins)
  - AXIS-X09 (15000$, 18-30 coins)
  
- **Purchase Logic Update**: Added a check that prevents users from purchasing a mining device if they already own a better or equally powerful one. 
   
### Fixed
- **User Data Management**: Improved the loading and saving of user data to prevent errors in edge cases.
- **Mining Status Fix**: Fixed an issue where users could start mining without a mining device or while already mining.
  
### Changed
- **Shop Command**: Updated the `.shop` command to reflect the changes in mining device options and prices.
