# Flutter Cursor Rules

This repository is a Cursor Plugin. It stores reusable Dart/Flutter agent rules as separate `.mdc` files, so they can be installed in any Flutter project.

These files do not replace a project's own `.cursor/rules` or `AGENTS.md`. Project-specific documents, such as PRD paths, stay in each app.

## Install

In Cursor, open Customize / Plugins and add this GitHub repository:

https://github.com/powerfulseed1998/cursor-flutter-rules

You can also clone the repository and add it as a local plugin.

## Rule files

| File | Purpose |
| --- | --- |
| `rules/coding-standards.mdc` | Page split, i18n, theme, naming |
| `rules/dart-primary-constructors.mdc` | Dart 3.13 primary constructors |
| `rules/design-standards.mdc` | Figma to Flutter |
| `rules/project-structure.mdc` | Feature-first `lib/` layout |
| `rules/state-management.mdc` | Riverpod and `setState` limits |
| `rules/version-control.mdc` | Git commit messages |
