@echo off
title Fortnite Log Reader
if ""=="%1" (
    "%~f0" CALLED < nul
) else (
    py -B main.py
    exit /b
)