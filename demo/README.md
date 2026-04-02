# demo/

This directory is available as a convenient location to store a local test video.

## Usage

Place any video file here and pass it to `detect_live.py` with `--source`:

```bash
cp /path/to/your/video.mp4 demo/sample.mp4
python detect_live.py --source demo/sample.mp4
```

Or use an absolute path — the `demo/` directory is just a suggestion:

```bash
python detect_live.py --source /path/to/any/video.mp4
```

If you do not have a video file, use your webcam:

```bash
python detect_live.py --source 0
```

## Why is no sample video included?

Video files are too large for a Git repository. The app does not bundle one.
Running the app without `--source` prints usage instructions and exits cleanly — no stack trace.

**Free sample video sources:**
- [Pexels](https://www.pexels.com/videos/) — free stock footage (no sign-up required)
- [Coverr](https://coverr.co/) — free commercial video clips
- Your own phone camera footage works perfectly

## Supported formats

Any format that OpenCV can read: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`.
