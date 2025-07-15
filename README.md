# ePython Lab – Content Creation Platform

A modern Flask-based content management platform supporting user roles, JWT authentication, and Tailwind CSS for a sleek, responsive UI. Built for tutorials, documentation, and content-driven applications.

---

## Features

- User authentication with local username and password
- Role-Based Access Control (admin, editor, viewer)
- JWT Access and Refresh Tokens
- Modern UI with Tailwind CSS and Dark Mode support
- Rich text editing with Quill.js including custom alert blocks
- RESTful API with Swagger documentation
- Client-side data fetching with Axios (ESM)
- CLI command to create a default admin user

---

## Technology Stack

- Backend: Python, Flask, SQLAlchemy, Marshmallow
- Frontend: Tailwind CSS, Quill.js
- Authentication: Flask-JWT-Extended (JWT)
- Database: SQLite by default (PostgreSQL supported)
- API Client: Axios

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/epython-lab.git
cd epython-lab
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR
.venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file or export environment variables directly.

```bash
export FLASK_APP=app
export FLASK_ENV=development

export ADMIN_USERNAME=admin
export ADMIN_EMAIL=admin@example.com
export ADMIN_PASSWORD=admin123

# Other config variables like DATABASE_URL, JWT_SECRET_KEY, etc.
```

---

## Running the Application

```bash
python3 run.py
```

Access the app at [http://localhost:5000](http://localhost:5000).

---

## Creating the Default Admin User

To initialize the application with a default admin user who has full administrative rights, run:

```bash
flask create-admin
flask seed-roles
```

This command will:

- Create the 'admin' role if it does not exist.
- Create the admin user with username, email, and password as defined in your environment variables.
- Assign the 'admin' role to this user.

If the admin user already exists, it will notify you accordingly.

### Example Output

```
🛠️ Created 'admin' role.
✅ Admin user 'admin' created.
```

Or if user exists:

```
ℹ️ Admin user already exists.
```

---

## API Documentation

Swagger UI is available at:

```
http://localhost:5000/docs
```

---

## Frontend

- Login and registration pages use Tailwind CSS for a modern and responsive design.
- Axios (ESM) is used for API calls.
- Quill.js provides a rich text editor with custom alert blocks.

---

## Testing

You can add tests using your preferred framework (e.g., pytest).

---

## Contribution

Feel free to open issues or submit pull requests for improvements and bug fixes.

---

## License

This project is licensed under the MIT License.

---

## Contact

Your Name — [your.email@example.com](mailto:your.email@example.com)

Project Link: https://github.com/yourusername/epython-lab

---
