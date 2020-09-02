# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added

## [0.0.1] - 2019-03-05
### Added
- Basic functionality for GitLab User Entity

## [0.0.2] - 2019-03-06
### Added
- Subcommand `dua` -> delete unconfirmed accounts

## [0.0.3] - 2019-04-06
### Added
- Subcommand `sac` -> find spam accounts

## [0.0.4] - 2019-04-24
### Renamed
- Subcommand `sac` -> `bsa`

## [0.4.0] - 2019-05-02
### Added
- Subcommand `gfe` -> get former external accounts

## [0.5.0] - 2019-05-06
### Added
- Subcommand `ffe` -> fix false external accounts

## [0.6.0] - 2019-05-06
### Added
- Subcommand `bsa` -> add --cron switch

## [0.7.0] - 2019-06-17
### Added
- Subcommand `bsa` -> discard spam cache

## [0.7.1] - 2019-11-25
### Fixed
- Subcommand `bsa` -> stronger spam rules

## [0.8.0] - 2019-12-05
### Fixed
- Subcommand `cla` -> check ldap accounts

## [0.9.0] - 2019-12-26
### Fixed
- Subcommand `dba` -> delete blocked accounts

## [0.10.0] - 2019-12-27
### Improved
- Subcommand `cla` -> delete unknown accounts

## [0.10.1] - 2020-05-28
### Improved
- Subcommand `bsa` -> Catch exception
  - gitlab.exceptions.GitlabBlockError: 500: Notification email can't be blank. Notification email is invalid
  
## [0.10.2] - 2020-05-29
### Improved
- Subcommand `bsa` -> stop blocking migration-bot

## [0.10.3] - 2020-06-02
### Improved
- Subcommand `dua` -> ignore known bots

## [0.10.4] - 2020-06-02
### Fixed
- Subcommand `dua` -> ValueError: unconverted data remains: Z

## [0.10.5] - 2020-06-02
### Fixed
- Subcommand `bsa` -> ignore alert-bot

## [0.10.6] - 2020-07-28
### Fixed
- Subcommand `bsa` -> ignore accounts without email

## [0.11.0] - 2020-06-02
### Fixed
- Subcommand `bsa` -> ignore support-bot

## [0.11.1] - 2020-09-02
### Fixed
- Subcommand `dua` -> time zone mismatch
