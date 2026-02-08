# How to Manage the CCL List

A tool has been created to make managing the list easy without editing JSON files.

## Prerequisites
You need Python installed (which you already have).

## How to use
1. Double-click `run_manager.bat` (or run `python manage_list.py` in cmd).
2. The "GDPS List Manager" window will open.

### Features
- **Levels Tab**:
  - Add new levels.
  - Edit existing levels (Names, IDs, Passwords, Video links, Records).
  - Reorder levels (Move Up/Down).
  - Delete levels.
  - **IMPORTANT**: Click "SAVE ALL CHANGES" at the top right to save the level order! (Individual level edits save immediately when you click "Save Level" in the popup).

- **Editors Tab**:
  - Edit the `_editors.json` file directly to add/remove editors.

- **Requirements Tab**:
  - Edit the submission requirements. Each line is a new bullet point on the site.

## Website Updates
- When you save changes in the manager, the `data/` files are updated immediately.
- If you are testing locally, just refresh the page.
- If you are hosting this on GitHub Pages, you need to `git commit` and `git push` the changes in the `data/` folder.
