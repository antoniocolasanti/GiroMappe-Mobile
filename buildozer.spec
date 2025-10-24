[app]
title = GiroMappe Mobile
package.name = giromappe
package.domain = org.example
source.dir = .
source.include_exts = py,kv
source.include_patterns = app/**,mobile_kivy/**

requirements = python3,kivy==2.3.0,kivymd==1.2.0,sqlite3,pillow,sqlalchemy,sqlmodel,pydantic,pydantic-settings,structlog

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]
log_level = 2
warn_on_root = 1
