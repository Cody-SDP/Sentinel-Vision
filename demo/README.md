# demo/

This directory is the default location for sample input files.

## Quick start

Place any short video file here and name it `sample.mp4`:

```bash
cp /path/to/your/video.mp4 demo/sample.mp4
```

Then run:

```bash
python detect_live.py
```

## Why is sample.mp4 not included?

Video files are too large for a Git repository. You can use any `.mp4`, `.avi`,
or `.mov` clip — even a 5–10 second clip works fine for a demo.

**Free sample video sources:**
- [Pexels](https://www.pexels.com/videos/) — free stock footage (no sign-up required)
- [Coverr](https://coverr.co/) — free commercial video clips
- Your own phone camera footage works perfectly

## Supported formats

Any format that OpenCV can read works: `.mp4`, `.avi`, `.mov`, `.mkv`, `.webm`.
