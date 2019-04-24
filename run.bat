set base_dir=%~dp0
set python=%base_dir%\venv\Scripts\python.exe
%python% %base_dir%\logs-downloader.py
%python% %base_dir%\logs-analyzer.py
%python% %base_dir%\logs-analyzer-non-gossip.py
