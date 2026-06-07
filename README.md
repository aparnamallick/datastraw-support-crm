# Datastraw Support CRM

A fully functional web-based customer support management system built for the Datastraw hiring assignment.

## Tech Stack
* **Backend:** Python, FastAPI, SQLAlchemy
* **Database:** SQLite
* **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript (Single-Page Application)

## Features
* **Create Tickets:** Capture customer details and issue descriptions automatically generating a unique ID.
* **Dashboard View:** List all tickets with a clean, responsive UI.
* **Live Search & Filter:** Debounced search functionality across names, IDs, emails, and descriptions, alongside status filtering.
* **Ticket Management:** Update ticket statuses (Open, In Progress, Closed) and add time-stamped internal interaction notes.

## Local Setup Instructions

1. **Clone the repository**
   \`\`\`bash
   git clone <YOUR_REPO_URL>
   cd <YOUR_REPO_NAME>
   \`\`\`

2. **Set up a virtual environment**
   \`\`\`bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
   \`\`\`

3. **Install dependencies**
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

4. **Run the server**
   \`\`\`bash
   uvicorn main:app --reload
   \`\`\`
   The database (`crm.db`) will automatically generate on the first run.

5. **Access the Application**
   * App UI: `http://127.0.0.1:8000`
   * API Docs: `http://127.0.0.1:8000/docs`
