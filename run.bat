@echo off
call env\Scripts\activate

uvicorn app.main:app --reload



pause
