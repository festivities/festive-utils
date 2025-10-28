@echo off

set "MODEL_NAME=large-v3-turbo"
set "CACHE_DIR=E:/Program Files/stable-ts/models"

set "XDG_CACHE_HOME=%CACHE_DIR%"

call "E:\Program Files\stable-ts\.venv\Scripts\activate.bat"

set "IN=%~1"
set "OUTDIR=%~dp1"

stable-ts "%IN%" --model "%MODEL_NAME%" --language en --max_words 4 --word_level False --refine --output_format srt --output_dir "%OUTDIR%"

pause
