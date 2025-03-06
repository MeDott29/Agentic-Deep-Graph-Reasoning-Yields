# Scripts Directory

This directory contains utility scripts for the Knowledge Graph Social Network System.

## Available Scripts

### `init_db.py`

Initializes the database with sample data for testing and development purposes. This script creates:

- Sample users with different interests and preferences
- Sample content items with titles, descriptions, and hashtags
- Sample interactions between users (follows, likes, comments)
- Sample interest nodes and connections to users

To run the script:

```bash
python src/scripts/init_db.py
```

The script will ask for confirmation before resetting existing data.

### Future Scripts

Additional utility scripts will be added here as the project evolves, such as:

- Data migration scripts
- Performance testing scripts
- Backup and restore scripts
- Analytics data generation scripts 