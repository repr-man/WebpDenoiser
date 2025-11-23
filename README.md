# Webp Reconstruction

A set of tools for training machine learning models that remove compression artifacts from Webp
images.

## Help! I'm lost!

- `backend` - This is where all the Python stuff is.  It contains all the machine learning training,
              evaluation, etc.  It also contains a Flask server that talks to the `frontend`.
- `frontend` - This is where the human evaluation tools are located.  It contains an Electron app
               that allows humans to inspect their data at various phases of the image transformation.

## Great! What do I need to get started?

- A Python distribution with a package manager.  For example:
    - Plain old `pip` with a virtual environment
    - `uv`
    - Any other packaging system compatible with `pyproject.toml` will probably work
- A JavaScript package manager and runtime.  For example:
    - `npm`
    - `pnpm`
    - `bun`

## Okay. I installed my package managers.  Now what?

It's time to download our dependencies and dataset.  Open your terminal and navigate into the same
directory that contains this README file.  We will show the commands to run using `pip` and `npm`.
If you are using different tools (e.g. `bun` and `uv`), we trust that you will know how to translate
them.  ;)

```shell
cd backend
python -m venv .

# On Windows:
.venv\Scripts\activate
# On Posix:
source .venv/bin/activate

pip install flask flask_cors numpy pillow typer requests huggingface_hub opencv-python torch
python main.py dataset
# Then follow the prompts.
```

When that's done, you can open up another terminal window and navigate to the directory with
the README again.  Then run:

```shell
cd frontend
npm install
```

Now, the world is your oyster.

## Groovy! What do I do when I want to inspect my images?

Start in your Python terminal (remember to activate the venv!).

```shell
python main.py server
```

Then switch over to your JavaScript terminal.

```shell
npm run dev
```

The Electron window should open, and you'll be off to the races.

## Nifty! What about when I want to train and evaluate my model?

Run the following in your Python terminal:

```shell
python main.py train
```

## Interjection!

When you want to learn more about the structure of each portion of the project, you can read the
README.md files in the `backend` and `frontend` directories.
