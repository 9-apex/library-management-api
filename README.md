# Library Management System API

A REST API for managing books, authors, and categories using Django REST Framework.

## Features

- Manage books, authors, and categories
- Register users and authenticate with JWT
- Public read access; administrator-only create, update, and delete
- Search, filtering, and pagination
- Django Admin and automated tests

## Setup

Install dependencies with `pip install -r requirements.txt`, then run `python manage.py migrate`.

Create an administrator with `python manage.py createsuperuser`, then start the server with `python manage.py runserver`.

## Tests

Run `python manage.py check` and `python manage.py test`.

## Endpoints

- Books: `/api/books/`
- Authors: `/api/authors/`
- Categories: `/api/categories/`
- Register: `/api/register/`
- Login and JWT tokens: `/api/login/`
- Refresh token: `/api/token/refresh/`
- User profile: `/api/profile/`
- Admin panel: `/admin/`

For protected requests, send the access token as `Authorization: Bearer ACCESS_TOKEN`.