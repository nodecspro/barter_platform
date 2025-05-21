# Barter Platform

This is a web application for a barter platform built with Django.

## Prerequisites

Before you begin, ensure you have met the following requirements:

*   Python 3.x installed
*   pip (Python package installer) installed

## Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/nodecspro/barter_platform
    cd barter_platform
    ```

2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Navigate to the project's root directory if you are not already there:

    ```bash
    cd barter_platform
    ```

2.  Apply database migrations:

    ```bash
    python manage.py migrate
    ```

3.  (Optional) Create a superuser to access the Django admin panel:

    ```bash
    python manage.py createsuperuser
    ```

    Follow the prompts to set up the superuser account.

## Running the Project

To run the development server, navigate to the project's root directory and execute:

```bash
python manage.py runserver
```

The application should now be accessible at `http://127.0.0.1:8000/`.
