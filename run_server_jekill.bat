@echo off
REM Запуск Jekyll в фоне (без окна)
start /B bundle exec jekyll serve --watch --livereload

REM Запуск Telegram бота в фоне (без окна)
start /B python "D:\privateseo.github.io\privseo_tg_bot\privseobot.py"

echo Оба процесса запущены в фоне.
echo Для остановки: 1) Закройте это окно 2) Найдите и завершите процессы в Диспетчере задач.
pause