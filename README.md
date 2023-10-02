#### EtL-проект по агрегации данных о вакансиях с Upwork и HeadHunter
#### О проекте
EtL-проект для круглосуточного отслеживания новых вакансий, их извлечения, обработки и загрузки в базу данных.
Источниками данных служат: API сайта https://www.upwork.com (международная платформа для поиска работы и размещения вакансий) и API сайта https://www.headhunter.ru.
#### ПО и IT-технологии используемые в проекте:
* OS: Linux (Ubuntu 22.04) / Windows 10
* Язык программирования: Python 3.10
* Язык запросов: SQL
* СУБД: PostgreSQL 14.9 / SQLight
* Автоматизация процесса: Apache Airflow 2.7.1
--- 
#### EtL project to aggregate data about job vacancies from Upwork and HeadHunter
#### About project
EtL-project to keep track of new vacancies round-the-clock, ingest, process and load them into the database.
The data sources are: the API of the site https://www.upwork.com (an international platform for finding jobs and posting vacancies) and the API of the site https://www.headhunter.ru.
#### Software and IT technologies used in the project
* OS: Linux (Ubuntu 22.04) / Windows 10
* Programming language: Python 3.10
* Query language: SQL
* DBMS: PostgreSQL 14.9 / SQLight
* Workflow orchestration: Apache Airflow 2.7.1
---
#### EtL diagram / Схема EtL процесса
![EtL_scheme](https://github.com/DE-Alex/EtL_jobs/assets/139635578/6ad1f7af-1b75-499b-a3ec-31fb93b926d6)
---
#### План работ на октябрь.
1. Портировать скрипты для HeadHunter на Linux. Сделать DAG. Срок: 05.10.23.
2. Мигрировать собранные на НН данные из SQLight в PostgreSQL. Срок: 7.10.23.
3. Зарегистрироваться на Yandex DataLens. Сделать скрипт по загрузке данных в облако. Срок: 12.10.23.
4. Сделать диаграммы с ключевыми метриками собранных данных. Срок: 20.10.23.
5. Сделать диаграмму с демонстрацией образцов собранных данных. Срок: 20.10.23.
6. Сделать диаграмму с ключевыми метриками EtLT процесса на основе данных AirFlow. Срок: 25.10.23.
7. Сделать скрипт резервного копирования данных. Срок: 31.10.23.
