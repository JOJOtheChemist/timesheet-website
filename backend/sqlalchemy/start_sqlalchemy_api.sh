#!/bin/bash
cd /home/ubuntu/timesheet/backend/sqlalchemy
export DATABASE_URL="sqlite:///./timesheet_sqlalchemy.db"
python main.py
