# Barter Platform

[English](#english) | [Русский](#русский)

<a name="english"></a>
# English

This is a web application for a barter platform built with Django.

## Table of Contents
- [Barter Platform](#barter-platform)
- [English](#english)
  - [Table of Contents](#table-of-contents)
  - [Virtual Environment](#virtual-environment)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Project](#running-the-project)
  - [Running Tests](#running-tests)
- [Русский](#русский)
  - [Оглавление](#оглавление)
  - [Виртуальное окружение](#виртуальное-окружение)
  - [Необходимые условия](#необходимые-условия)
  - [Установка](#установка)
  - [Конфигурация](#конфигурация)
  - [Запуск проекта](#запуск-проекта)
  - [Запуск тестов](#запуск-тестов)

<a name="english-virtual-environment"></a>
## Virtual Environment

It is recommended to use a virtual environment to manage project dependencies.

1.  Create a virtual environment:

    ```bash
    python -m venv venv
    ```

2.  Activate the virtual environment:

    *   On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    *   On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

<a name="english-prerequisites"></a>
## Prerequisites

Before you begin, ensure you have met the following requirements:

*   Python 3.x installed
*   pip (Python package installer) installed

<a name="english-installation"></a>
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

<a name="english-configuration"></a>
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

<a name="english-running-the-project"></a>
## Running the Project

To run the development server, navigate to the project's root directory and execute:

```bash
python manage.py runserver
```

The application should now be accessible at `http://127.0.0.1:8000/`.

<a name="english-running-tests"></a>
## Running Tests

To run the project's tests, navigate to the project's root directory and execute:

```bash
python manage.py test
```

---

<a name="русский"></a>
# Русский

Это веб-приложение для платформы обмена, созданное с использованием Django.

## Оглавление
- [Barter Platform](#barter-platform)
- [English](#english)
  - [Table of Contents](#table-of-contents)
  - [Virtual Environment](#virtual-environment)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Project](#running-the-project)
  - [Running Tests](#running-tests)
- [Русский](#русский)
  - [Оглавление](#оглавление)
  - [Виртуальное окружение](#виртуальное-окружение)
  - [Необходимые условия](#необходимые-условия)
  - [Установка](#установка)
  - [Конфигурация](#конфигурация)
  - [Запуск проекта](#запуск-проекта)
  - [Запуск тестов](#запуск-тестов)

<a name="русский-виртуальное-окружение"></a>
## Виртуальное окружение

Рекомендуется использовать виртуальное окружение для управления зависимостями проекта.

1.  Создайте виртуальное окружение:

    ```bash
    python -m venv venv
    ```

2.  Активируйте виртуальное окружение:

    *   В Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    *   В macOS и Linux:

        ```bash
        source venv/bin/activate
        ```

<a name="русский-необходимые-условия"></a>
## Необходимые условия

Прежде чем начать, убедитесь, что у вас установлены следующие компоненты:

*   Установлен Python 3.x
*   Установлен pip (установщик пакетов Python)

<a name="русский-установка"></a>
## Установка

1.  Клонируйте репозиторий:

    ```bash
    git clone https://github.com/nodecspro/barter_platform
    cd barter_platform
    ```

2.  Установите необходимые пакеты Python:

    ```bash
    pip install -r requirements.txt
    ```

<a name="русский-конфигурация"></a>
## Конфигурация

1.  Перейдите в корневой каталог проекта, если вы еще не там:

    ```bash
    cd barter_platform
    ```

2.  Примените миграции базы данных:

    ```bash
    python manage.py migrate
    ```

3.  (Необязательно) Создайте суперпользователя для доступа к панели администратора Django:

    ```bash
    python manage.py createsuperuser
    ```

    Следуйте инструкциям для настройки учетной записи суперпользователя.

<a name="русский-запуск-проекта"></a>
## Запуск проекта

Для запуска сервера разработки перейдите в корневой каталог проекта и выполните:

```bash
python manage.py runserver
```

Приложение должно быть доступно по адресу `http://127.0.0.1:8000/`.

<a name="русский-запуск-тестов"></a>
## Запуск тестов

Для запуска тестов проекта перейдите в корневой каталог проекта и выполните:

```bash
python manage.py test
