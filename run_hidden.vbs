WScript.Sleep 30000  ' Ждем 30 секунд после входа в систему
Set WshShell = CreateObject("WScript.Shell")

' Запуск Jekyll в фоне
WshShell.Run "cmd /c bundle exec jekyll serve --watch --livereload", 0, False

' Запуск Telegram бота в фоне (с задержкой 3 секунды)
WScript.Sleep 3000
WshShell.Run "cmd /c python ""D:\privateseo.github.io\privseo_tg_bot\privseobot.py""", 0, False

' Самоуничтожение скрипта
Set WshShell = Nothing