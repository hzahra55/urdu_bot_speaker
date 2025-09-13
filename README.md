0. Setup environment by python -m venv venv.

1. `pip install -r requirements.txt` (install required libraries).

2. `python agent.py download-files` (setup the offline model stuff needed.)

3. Setup the keys in `.env` file:
   - `OPENAI_API_KEY` (get this from https://platform.openai.com/account/api-keys)
   - `UPLIFTAI_API_KEY` (get this from https://platform.upliftai.org/studio/home)
   - `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` (get these from https://livekit.io/ by creating a free account, and visit API keys page)

4. Start agent multiple options:
  - `python agent.py console` -> talk directly in the console
  - `python agent.py dev` -> talk through web interface 
  terminal-1 : uvicorn token_server:app --host 0.0.0.0 --port 8787 --reload
  terminal-2 : python agent.py dev
  terminal-3 : go to web folder and run python -m http.server 8080
               then open http://localhost:8080/index.html
               