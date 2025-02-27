# Library Service

Clone repo and install requirements:
````bash
  git clone https://github.com/MindDevastation/library-service-project.git
````
Change brunch to `develop`

Change folder to src:
````bash
  cd src
````

Run:

````bash
  pip install -r requrements.txt
````

## Add auto code styling

Run:

```bash
  pre-commit install
```

It will run `black` every time you make a commit

Also you can 
- Open `File` → `Settings` → `Tools` → `Black`
- Check the `Enable Black`
- Go to `File` → `Settings` → `Editor` → `Editor` → `Code Style` → `Python` and 
make sure that `Formatter` is set to `Black`

Now black will format the code when you press `Ctrl + Alt + L`.

## Project structure

<pre>
library-service-project/
├── src/
│   ├── library/       # Main project (settings, routes)
│   ├── users/         # User management application
│   ├── books/         # Book management application
│   ├── borrowings/    # Booking management application
│   ├── payments/      # Payment application
│   ├── logs/          # System Logs
│   ├── templates/     # Email templates (e.g., return reminders)
│   ├── library_db_data.json  # Initial data (optional)
│   └── manage.py
├── requirements.txt   # Dependencies
├── Dockerfile         # Containerization
├── docker-compose.yml # Конфигурация Docker
├── .env               # Environment variables
├── .gitignore         # Ignored files
├── README.md          # Documentation
└── .pre-commit-config.yaml  # Pre-commit hooks
</pre>

| Микросервис на диаграмме | 	Соответствие в Django монолите |
|--------------------------|---------------------------------|
| 📖 Books Service         | 	books (Django app)             |
| 📌 Borrowing Service     | 	borrowings (Django app)        |
| 👥 Customers Service     | 	users (Django app)             |
| 👀 View Service          | 	DRF Browsable API (auto UI)    |
| 💰 Payment Service       | 	payments (Django app)          |
| 📢 Notifications Service | 	Celery + Django Signals        |

## Users (Arseniy)

- Email -> unique -> login
- First name
- Last name
- Password
- Is staff

## Borrowing (Taras)

- Borrow date
- Expected Return date
- Actual Return date
- Book id -> Books 1-1
- User id -> Users 1-1

## Payment (Nick)

- Status
- Type
- Borrowing id -> Borrowing
- Session url
- Session id
- Money to pay

## Books (Oleksandr)

- Title
- Pages
- Authors
- Cover
- Inventory
- Daily fee
- Quantity

## Telegram bot (Alex)

## Mailing (Ruslan)
